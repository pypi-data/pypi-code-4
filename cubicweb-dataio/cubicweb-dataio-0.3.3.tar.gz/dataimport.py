# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.

""" Te Massive Store is a CW store used to push massive amounts of data using
pure SQL logic, thus avoiding CW checks. It is faster than other CW stores
(it does not check the eid at each step, it uses the COPY FROM method), but is less safe
(no data integrity securities), and does not return an eid while using
create_entity function.

WARNING:

   - This store may be only used with PostgreSQL for now, as it relies
     on the COPY FROM method, and on specific PostgreSQL tables to get all
     the indexes.
   - This store can only insert relations that are not inlined (i.e.,
     which do *not* have inlined=True in their definition in the schema).


 It should be used as follows:

    store = MassiveObjectStore(session)
    store.init_rtype_table('Person', 'lives_in', 'Location')
    ...
    store.create_entity('Person', subj_iid_attribute=person_iid, ...)
    store.create_entity('Location', obj_iid_attribute=location_iid, ...)
    ...

    # subj_iid_attribute and obj_iid_attribute are argument names
    # chosen by the user (e.g. "cwuri"). These names can be identical.
    # person_iid and location_iid are unique IDs and depend on the data
    # (e.g URI).

    store.flush()
    store.relate_by_iid(person_iid, 'lives_in', location_iid)
    ...
    # For example:
    store.create_entity('Person',
                        cwuri='http://dbpedia.org/toto',
                        name='Toto')
    store.create_entity('Location',
                        uri='http://geonames.org/11111',
                        name='Somewhere')
    ...
    store.flush()
    store.relate_by_iid('http://dbpedia.org/toto',
                        'lives_in',
                        'http://geonames.org/11111')
    # Finally
    store.flush_meta_data()
    store.convert_relations('Person', 'lives_in', 'Location',
                            'subj_iid_attribute', 'obj_iid_attribute')
    # For the previous example:
    store.convert_relations('Person', 'lives_in', 'Location', 'cwuri', 'uri')
    store.cleanup()

"""
import logging
from StringIO import StringIO
from datetime import datetime
from collections import defaultdict
from psycopg2 import ProgrammingError

from yams.constraints import SizeConstraint

from cubicweb.utils import make_uid
from cubicweb.server.sqlutils import SQL_PREFIX
import cubicweb.dataimport as cwdi

from cubes.dataio.interfaces import URI_RDF_PROP, normalize_xml


################################################################################
### UTILITY FUNCTIONS  #########################################################
################################################################################
def fast_delete_eids(session, etype, eids, chunksize=10000):
    """ Complete delete etype given eids
    """
    eids = list(eids)
    for i in range(0, len(eids), chunksize):
        _eids = eids[i:i+chunksize]
        if not _eids:
            break
        str_eids = ','.join(str(eid) for eid in _eids)
        etype_eid = session.find_one_entity('CWEType', name=etype).eid
        session.system_sql('DELETE FROM cw_%s WHERE cw_eid IN (%s)'
                           % (etype.lower(), str_eids))
        for table in ('is_relation', 'is_instance_of_relation',
                      'cw_source_relation', 'owned_by_relation', 'created_by_relation'):
            session.system_sql("DELETE FROM %s WHERE eid_from IN (%s)"
                               % (table, str_eids))
        session.system_sql("DELETE FROM entities WHERE eid IN (%s)" % str_eids)
    session.commit()

def check_if_table_exists(session, table_name, pg_schema='public'):
    sql = "SELECT * from information_schema.tables WHERE table_name=%(t)s AND table_schema=%(s)s"
    crs = session.system_sql(sql, {'t': table_name, 's': pg_schema})
    res = crs.fetchall()
    if res:
        return True
    return False

def check_if_primary_key_exists_for_table(session, table_name, pg_schema='public'):
    sql = ("SELECT constraint_name FROM information_schema.table_constraints "
           "WHERE constraint_type = 'PRIMARY KEY' AND table_name=%(t)s AND table_schema=%(s)s")
    crs = session.system_sql(sql, {'t': table_name, 's': pg_schema})
    res = crs.fetchall()
    if res:
        return True
    return False

def get_index_query(session, name, pg_schema='public'):
    """Get the request to be used to recreate the index"""
    return session.system_sql("SELECT pg_get_indexdef(c.oid) "
                              "from pg_catalog.pg_class c "
                              "LEFT JOIN pg_catalog.pg_namespace n "
                              "ON n.oid = c.relnamespace "
                              "WHERE c.relname = %(r)s AND n.nspname=%(n)s",
                              {'r': name, 'n': pg_schema}).fetchone()[0]

def get_constraint_query(session, name, pg_schema='public'):
    """Get the request to be used to recreate the constraint"""
    return session.system_sql("SELECT pg_get_constraintdef(c.oid) "
                              "from pg_catalog.pg_constraint c "
                              "LEFT JOIN pg_catalog.pg_namespace n "
                              "ON n.oid = c.connamespace "
                              "WHERE c.conname = %(r)s AND n.nspname=%(n)s",
                              {'r': name, 'n': pg_schema}).fetchone()[0]

def get_application_indexes(session, tablename, pg_schema='public'):
    """ Iterate over all the indexes """
    # This SQL query (cf http://www.postgresql.org/message-id/432F450F.4080700@squiz.net)
    # aims at getting all the indexes for each table.
    sql = '''SELECT c.relname as "Name",
    CASE c.relkind WHEN 'r' THEN 'table' WHEN 'v' THEN 'view' WHEN 'i' THEN 'index'
    WHEN 'S' THEN 'sequence' WHEN 's' THEN 'special' END as "Type",
    c2.relname as "Table"
    FROM pg_catalog.pg_class c
    JOIN pg_catalog.pg_index i ON i.indexrelid = c.oid
    JOIN pg_catalog.pg_class c2 ON i.indrelid = c2.oid
    LEFT JOIN pg_catalog.pg_user u ON u.usesysid = c.relowner
    LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('i','')
    AND c2.relname = '%s'
    AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
    AND pg_catalog.pg_table_is_visible(c.oid)
    ORDER BY 1,2;''' % tablename
    indexes_list = session.system_sql(sql).fetchall()
    indexes = {}
    for name, type, table in indexes_list:
        indexes[name] = get_index_query(session, name, pg_schema)
    return indexes

def get_application_constraints(session, tablename, pg_schema='public'):
    """ Iterate over all the constraints """
    sql = '''SELECT i.conname as "Name", c.relkind, c2.relname as "Table"
             FROM pg_catalog.pg_class c JOIN pg_catalog.pg_constraint i
             ON i.conrelid = c.oid JOIN pg_catalog.pg_class c2 ON i.conrelid=c2.oid
             LEFT JOIN pg_catalog.pg_user u ON u.usesysid = c.relowner
             LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
             WHERE c2.relname = '%s' AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
             AND pg_catalog.pg_table_is_visible(c.oid)
             ORDER BY 1,2;''' % tablename
    indexes_list = session.system_sql(sql).fetchall()
    constraints = {}
    for name, type, table in indexes_list:
        query = get_constraint_query(session, name, pg_schema)
        constraints[name] = 'ALTER TABLE %s ADD CONSTRAINT %s %s' % (tablename, name, query)
    return constraints

def get_application_indexes_constraints(session, tablename, pg_schema='public'):
    """ Get all the indexes/constraints for a given tablename """
    indexes = get_application_indexes(session, tablename, pg_schema)
    constraints = get_application_constraints(session, tablename, pg_schema)
    _indexes = {}
    for name, query in indexes.iteritems():
        # Remove pkey indexes (automatically created by constraints)
        # Specific cases of primary key, see #3224079
        if name not in constraints:
            _indexes[name] = query
    return _indexes, constraints


################################################################################
### CONSTRAINTS MANAGEMENT FUNCTIONS  ##########################################
################################################################################
def get_size_constraints(schema):
    """analyzes yams ``schema`` and returns the list of size constraints.

    The returned value is a dictionnary mapping entity types to a
    sub-dictionnaries mapping attribute names -> max size.
    """
    size_constraints = {}
    # iterates on all entity types
    for eschema in schema.entities():
        # for each entity type, iterates on attribute definitions
        size_constraints[eschema.type] = eschema_constraints = {}
        for rschema, aschema in eschema.attribute_definitions():
            # for each attribute, if a size constraint is found,
            # append it to the size constraint list
            maxsize = None
            rdef = rschema.rdef(eschema, aschema)
            for constraint in rdef.constraints:
                if isinstance(constraint, SizeConstraint):
                    maxsize = constraint.max
                    eschema_constraints[rschema.type] = maxsize
    return size_constraints

def get_default_values(schema):
    """analyzes yams ``schema`` and returns the list of default values.

    The returned value is a dictionnary mapping entity types to a
    sub-dictionnaries mapping attribute names -> default values.
    """
    default_values = {}
    # iterates on all entity types
    for eschema in schema.entities():
        # for each entity type, iterates on attribute definitions
        default_values[eschema.type] = eschema_constraints = {}
        for rschema, aschema in eschema.attribute_definitions():
            # for each attribute, if a size constraint is found,
            # append it to the size constraint list
            if eschema.default(rschema.type) is not None:
                eschema_constraints[rschema.type] = eschema.default(rschema.type)
    return default_values


################################################################################
### RELATION STORE MIXIN #######################################################
################################################################################
class RelationStoreMixin(object):
    """ Mixin for stores to implement the behavior of relation
    based on external id (e.g. uri)
    """

    def __init__(self, session, replace_sep='',
                 commit_at_flush=True, iid_maxsize=1024):
        """ Mixin for stores to implement the behavior of relation
        based on external id (e.g. uri)

        - session: CubicWeb session
        - replace_sep: String. Replace separator used for
          (COPY FROM) buffer creation.
        - commit_at_flush: Boolean. Commit after each flush().
        - iid_maxsize: Int. Max size of the iid, used to create the
                    iid_eid convertion table.
        """
        self.logger = logging.getLogger('dataio.relationmixin')
        self.session = session
        self.iid_maxsize = iid_maxsize
        self.replace_sep = replace_sep
        self.commit_at_flush = commit_at_flush
        self._data_uri_relations = defaultdict(list)
        self._initialized = {'init_uri_eid': set([]),
                             'uri_eid_inserted': set([]),
                             'uri_rtypes': set([])}


    ###########################################################################
    ### INIT FUNCTIONS ########################################################
    ###########################################################################
    def init_rtype_table(self, etype_from, rtype, etype_to):
        """ Build temporary table a for standard rtype """
        # Create an uri_eid table for each etype for a better
        # control of which etype is concerns for a particular
        # possibly multivalued relation.
        for etype in (etype_from, etype_to):
            if etype and etype not in self._initialized['init_uri_eid']:
                self._init_uri_eid_table(etype)
        if rtype not in self._initialized['uri_rtypes']:
            # Create the temporary tables
            if not self.rschema(rtype).inlined:
                try:
                    sql = 'CREATE TABLE %(r)s_relation_iid_tmp (uri_from character ' \
                          'varying(%(s)s), uri_to character varying(%(s)s))'
                    self.session.system_sql(sql % {'r': rtype, 's': self.iid_maxsize})
                except ProgrammingError:
                    # XXX Already exist (probably due to multiple import)
                    pass
            else:
                self.logger.warning("inlined relation %s: cannot insert it" % rtype)
            #Add it to the initialized set
            self._initialized['uri_rtypes'].add(rtype)

    def _init_uri_eid_table(self, etype):
        """ Build a temporary table for id/eid convertion
        """
        try:
            sql = "CREATE TABLE uri_eid_%(e)s (uri character varying(%(size)s), eid integer)"
            self.session.system_sql(sql % {'e': etype.lower(),
                                           'size': self.iid_maxsize,
                                           })
        except ProgrammingError:
            # XXX Already exist (probably due to multiple import)
            pass
        # Add it to the initialized set
        self._initialized['init_uri_eid'].add(etype)


    ###########################################################################
    ### RELATE FUNCTION #######################################################
    ###########################################################################
    def relate_by_iid(self, iid_from, rtype, iid_to):
        """Add new relation based on the internal id (iid)
        of the entities (not the eid)"""
        # Push data
        if isinstance(iid_from, unicode):
            iid_from = iid_from.encode('utf-8')
        if isinstance(iid_to, unicode):
            iid_to = iid_to.encode('utf-8')
        self._data_uri_relations[rtype].append({'uri_from': iid_from, 'uri_to': iid_to})


    ###########################################################################
    ### FLUSH FUNCTIONS #######################################################
    ###########################################################################
    def flush_relations(self):
        """ Flush the relations data
        """
        for rtype, data in self._data_uri_relations.iteritems():
            if not data:
                self.logger.info('No data for rtype %s' % rtype)
            buf = StringIO('\n'.join(['%(uri_from)s\t%(uri_to)s' % d for d in data]))
            if not buf:
                self.logger.info('Empty Buffer for rtype %s' % rtype)
                continue

            cursor = self.session.cnxset[self.source.uri]
            if not self.rschema(rtype).inlined:
                cursor.copy_from(buf, '%s_relation_iid_tmp' % rtype.lower(),
                                 null='NULL', columns=('uri_from', 'uri_to'))
            else:
                self.logger.warning("inlined relation %s: cannot insert it" % rtype)
            buf.close()
            # Clear data cache
            self._data_uri_relations[rtype] = []
            # Commit if asked
            if self.commit_at_flush:
                self.commit()

    def cleanup(self):
        """ Remove temporary tables and columns
        """
        self.logger.info("Start cleaning")
        # Cleanup tables
        for etype in self._initialized['init_uri_eid']:
            self.session.system_sql('DROP TABLE uri_eid_%s' % etype.lower())
        # Remove relations tables
        for rtype in self._initialized['uri_rtypes']:
            if not self.rschema(rtype).inlined:
                self.session.system_sql('DROP TABLE %(r)s_relation_iid_tmp' % {'r': rtype})
            else:
                self.logger.warning("inlined relation %s: no cleanup to be done for it" % rtype)
        self.commit()

    def fill_uri_eid_table(self, etype, uri_label):
        """ Fill the uri_eid table
        """
        self.logger.info('Fill uri_eid for etype %s' % etype)
        sql = 'INSERT INTO uri_eid_%(e)s SELECT cw_%(l)s, cw_eid FROM cw_%(e)s'
        self.session.system_sql(sql % {'l': uri_label, 'e': etype.lower()})
        # Add indexes
        self.session.system_sql('CREATE INDEX uri_eid_%(e)s_idx ON uri_eid_%(e)s'
                                '(uri)' % {'e': etype.lower()})
        # Set the etype as converted
        self._initialized['uri_eid_inserted'].add(etype)
        self.commit()

    def convert_relations(self, etype_from, rtype, etype_to,
                          uri_label_from='cwuri', uri_label_to='cwuri'):
        """ Flush the converted relations
        """
        # Always flush relations to be sure
        self.logger.info('Flush relations')
        self.flush_relations()
        if uri_label_from and etype_from not in self._initialized['uri_eid_inserted']:
            self.fill_uri_eid_table(etype_from, uri_label_from)
        if uri_label_to and etype_to not in self._initialized['uri_eid_inserted']:
            self.fill_uri_eid_table(etype_to, uri_label_to)
        if uri_label_from and uri_label_to:
            sql = '''INSERT INTO %(r)s_relation (eid_from, eid_to) SELECT DISTINCT O1.eid, O2.eid
            FROM %(r)s_relation_iid_tmp AS T, uri_eid_%(ef)s as O1, uri_eid_%(et)s as O2
            WHERE O1.uri=T.uri_from AND O2.uri=T.uri_to AND NOT EXISTS (
            SELECT 1 FROM %(r)s_relation AS TT WHERE TT.eid_from=O1.eid AND TT.eid_to=O2.eid);
            '''
        if uri_label_to and not uri_label_from:
            sql = '''INSERT INTO %(r)s_relation (eid_from, eid_to) SELECT DISTINCT
            CAST(T.uri_from AS INTEGER), O1.eid
            FROM %(r)s_relation_iid_tmp AS T, uri_eid_%(et)s as O1
            WHERE O1.uri=T.uri_to AND NOT EXISTS (
            SELECT 1 FROM %(r)s_relation AS TT WHERE
            TT.eid_from=CAST(T.uri_from AS INTEGER) AND TT.eid_to=O1.eid);
            '''
        if uri_label_from and not uri_label_to:
            sql = '''INSERT INTO %(r)s_relation (eid_from, eid_to) SELECT DISTINCT O1.eid, T.uri_to
            O1.eid, CAST(T.uri_to AS INTEGER)
            FROM %(r)s_relation_iid_tmp AS T, uri_eid_%(ef)s as O1
            WHERE O1.uri=T.uri_from AND NOT EXISTS (
            SELECT 1 FROM %(r)s_relation AS TT WHERE
            TT.eid_from=O1.eid AND TT.eid_to=CAST(T.uri_to AS INTEGER));
            '''
        try:
            if not self.rschema(rtype).inlined:
                self.session.system_sql(sql % {'r': rtype.lower(),
                                               'et': etype_to.lower() if etype_to else u'',
                                               'ef': etype_from.lower() if etype_from else u'',
                                               })
            else:
                self.logger.warning("inlined relation %s: cannot insert it" % rtype)
        except Exception as ex:
            self.logger.error("Cannot insert relation %s: %s" % (rtype, ex))
        self.commit()


################################################################################
### MASSIVE STORE  #############################################################
################################################################################
class MassiveObjectStore(cwdi.NoHookRQLObjectStore, RelationStoreMixin):
    """
    Store for massive import of data, with delayed insertion of meta data.

    WARNINGS:
   - This store may be only used with PostgreSQL for now, as it relies
     on the COPY FROM method, and on specific PostgreSQL tables to get all
     the indexes.
   - This store can only insert relations that are not inlined (i.e.,
     which do *not* have inlined=True in their definition in the schema).


   It should be used as follows:

       store = MassiveObjectStore(session)
       store.init_rtype_table('Person', 'lives_in', 'Location')
       ...

       store.create_entity('Person', subj_iid_attribute=person_iid, ...)
       store.create_entity('Location', obj_iid_attribute=location_iid, ...)
       ...

       # subj_iid_attribute and obj_iid_attribute are argument names
       # chosen by the user (e.g. "cwuri"). These names can be identical.
       # person_iid and location_iid are unique IDs and depend on the data
       # (e.g URI).
       store.flush()
       store.relate_by_iid(person_iid, 'lives_in', location_iid)
       # For example:
       store.create_entity('Person',
                           cwuri='http://dbpedia.org/toto',
                           name='Toto')
       store.create_entity('Location',
                           uri='http://geonames.org/11111',
                           name='Somewhere')
       store.flush()
       store.relate_by_iid('http://dbpedia.org/toto',
                       'lives_in',
                       'http://geonames.org/11111')
       # Finally
       store.flush_meta_data()
       store.convert_relations('Person', 'lives_in', 'Location',
                               'subj_iid_attribute', 'obj_iid_attribute')
       # For the previous example:
       store.convert_relations('Person', 'lives_in', 'Location', 'cwuri', 'uri')
       ...
       store.cleanup()
    """

    def __init__(self, session, autoflush_metadata=True,
                 replace_sep='', commit_at_flush=True,
                 drop_index=True,
                 pg_schema='public',
                 iid_maxsize=1024, uri_param_name='rdf:about',
                 eids_seq_range=10000, eids_seq_start=None,
                 on_commit_callback=None, on_rollback_callback=None,
                 slave_mode=False, build_entities=False):
        """ Create a MassiveObject store, with the following attributes:

        - session: CubicWeb session
        - autoflush_metadata: Boolean.
                              Automatically flush the metadata after
                              each flush()
        - replace_sep: String. Replace separator used for
                       (COPY FROM) buffer creation.
        - commit_at_flush: Boolean. Commit after each flush().
        - drop_index: Boolean. Drop SQL index before COPY FROM
        - eids_seq_range: Int. Range of the eids_seq_range to be fetched each time
                               by the store (default is 10000).
                               If None, the sequence eids is attached to each entity tables
                               (backward compatibility with the 0.2.0).
        - eids_seq_start: Int. Set the eids sequence value (if None, nothing is done).
        - iid_maxsize: Int. Max size of the iid, used to create the
                    iid_eid convertion table.
        - uri_param_name: String. If given, will use this parameter to get cw_uri
                          for entities.
        - build_entities: Boolean. If True, create_entity returns a CW etype object
          (but WITHOUT eid !).
        """
        super(MassiveObjectStore, self).__init__(session)
        RelationStoreMixin.__init__(self, session, iid_maxsize=iid_maxsize,
                                    replace_sep=replace_sep,
                                    commit_at_flush=commit_at_flush)
        self.logger = logging.getLogger('dataio.massiveimport')
        self.autoflush_metadata = autoflush_metadata
        self.replace_sep = replace_sep
        self.drop_index = drop_index
        self.slave_mode = slave_mode
        self.size_constraints = get_size_constraints(session.vreg.schema)
        self.default_values = get_default_values(session.vreg.schema)
        self._build_entities = build_entities
        self._data_entities = defaultdict(list)
        self._data_relations = defaultdict(list)
        self._etype_eclass_map_cache = {}
        self.pkey_dict = defaultdict(list)
        self._now = datetime.now()
        self._default_cwuri = make_uid('_auto_generated')
        self.uri_param_name = uri_param_name
        self._count_cwuri = 0
        self.commit_at_flush = commit_at_flush
        self.on_commit_callback = on_commit_callback
        self.on_rollback_callback = on_rollback_callback
        # Deals with pg schema, see #3216686
        self.pg_schema = pg_schema or 'public'
        # Initialized the meta tables of dataio for warm restart
        self._init_dataio_metatables()
        # Internal markers of initialization
        self._initialized['entities'] = set([])
        self._initialized['rtypes'] = set([])
        self._eids_seq = []
        self._eids_seq_range = eids_seq_range
        self._eids_seq_start = eids_seq_start
        if self._eids_seq_start:
            self.session.system_sql("SELECT setval('entities_id_seq', %(v)s)",
                                    {'v': self._eids_seq_start})
        # recreate then when self.cleanup() is called
        if not self.slave_mode:
            if self.drop_index:
                self._drop_metatables_constraints()

    def _init_dataio_metatables(self):
        """ Initialized the meta tables of dataio for warm restart
        """
        self._initialized_table_created = False
        self._constraint_table_created = False
        self._metadata_table_created = False
        # Check if dataio tables are not already created (i.e. a restart)
        crs = self.session.system_sql('SELECT tablename FROM pg_tables WHERE schemaname=%(s)s',
                                      {'s': self.pg_schema})
        tables = set([t for t, in crs.fetchall()])
        if 'dataio_initialized' in tables:
            self._initialized_table_created = True
        if 'dataio_constraints' in tables:
            self._constraint_table_created = True
        if 'dataio_metadata' in tables:
            self._metadata_table_created = True


    ###########################################################################
    ### SQL UTILITIES #########################################################
    ###########################################################################
    def drop_and_store_indexes_constraints(self, tablename):
        # Drop indexes and constraints
        if not self._constraint_table_created:
            # Create a table to save the constraints
            # Allow reload even after crash
            sql = "CREATE TABLE dataio_constraints (origtable text, query text, type varchar(256))"
            self.session.system_sql(sql)
            self._constraint_table_created = True
        self._drop_table_constraints_indexes(tablename)

    def _drop_table_constraints_indexes(self, tablename):
        """ Drop and store table constraints and indexes """
        indexes, constraints = get_application_indexes_constraints(self.session, tablename, self.pg_schema)
        for name, query in constraints.iteritems():
            sql = 'INSERT INTO dataio_constraints VALUES (%(e)s, %(c)s, %(t)s)'
            self.session.system_sql(sql, {'e': tablename, 'c': query, 't': 'constraint'})
            sql = 'ALTER TABLE %s DROP CONSTRAINT %s' % (tablename, name)
            self.session.system_sql(sql)
        for name, query in indexes.iteritems():
            sql = 'INSERT INTO dataio_constraints VALUES (%(e)s, %(c)s, %(t)s)'
            self.session.system_sql(sql, {'e': tablename, 'c': query, 't': 'index'})
            sql = 'DROP INDEX %s' % name
            self.session.system_sql(sql)

    def reapply_constraint_index(self, tablename):
        sql = 'SELECT query FROM dataio_constraints WHERE origtable = %(e)s'
        crs = self.session.system_sql(sql, {'e': tablename})
        for query, in crs.fetchall():
            self.session.system_sql(query)
            self.session.system_sql('DELETE FROM dataio_constraints WHERE origtable = %(e)s AND query = %(q)s' ,
                                    {'e': tablename, 'q': query})

    def _drop_metatables_constraints(self):
        """ Drop all the constraints for the meta data"""
        for tablename in ('entities', 'created_by_relation', 'owned_by_relation',
                          'is_instance_of_relation', 'identity_relation'):
            self.drop_and_store_indexes_constraints(tablename)

    def _create_metatables_constraints(self):
        """ Create all the constraints for the meta data"""
        for tablename in ('entities', 'created_by_relation', 'owned_by_relation',
                          'is_instance_of_relation', 'identity_relation'):
            # Indexes and constraints
            if self.drop_index:
                self.reapply_constraint_index(tablename)

    def init_relation_table(self, rtype):
        """ Get and remove all indexes for performance sake """
        # Create temporary table
        if not self.slave_mode and rtype not in self._initialized['rtypes']:
            sql = "CREATE TABLE %s_relation_tmp (eid_from integer, eid_to integer)" % rtype.lower()
            self.session.system_sql(sql)
            if self.drop_index:
                # Drop indexes and constraints
                tablename = '%s_relation' % rtype.lower()
                self.drop_and_store_indexes_constraints(tablename)
            # Push the etype in the initialized table for easier restart
            self.init_create_initialized_table()
            sql = 'INSERT INTO dataio_initialized VALUES (%(e)s, %(t)s)'
            self.session.system_sql(sql, {'e': rtype, 't': 'rtype'})
            # Mark rtype as "initialized" for faster check
            self._initialized['rtypes'].add(rtype)

    def init_create_initialized_table(self):
        """ Create the dataio initialized table
        """
        if not self._initialized_table_created:
            sql = "CREATE TABLE dataio_initialized (retype text, type varchar(128))"
            self.session.system_sql(sql)
            self._initialized_table_created = True

    def init_etype_table(self, etype):
        """ Add eid sequence to a particular etype table and
        remove all indexes for performance sake """
        if etype not in self._etype_eclass_map_cache:
            # Only for non-initialized etype and not slave mode store
            if not self.slave_mode:
                if self._eids_seq_range is None:
                    # Eids are directly set by the entities_id_seq.
                    # We attach this sequence to all the created etypes.
                    sql = ("ALTER TABLE cw_%s ALTER COLUMN cw_eid "
                           "SET DEFAULT nextval('entities_id_seq')" % etype.lower())
                    self.session.system_sql(sql)
                if self.drop_index:
                    # Drop indexes and constraints
                    tablename = 'cw_%s' % etype.lower()
                    self.drop_and_store_indexes_constraints(tablename)
                # Push the etype in the initialized table for easier restart
                self.init_create_initialized_table()
                sql = 'INSERT INTO dataio_initialized VALUES (%(e)s, %(t)s)'
                self.session.system_sql(sql, {'e': etype, 't': 'etype'})
            # Mark etype as "initialized" for faster check
            self._initialized['entities'].add(etype)
            # Add the etype class to the cache
            self._etype_eclass_map_cache[etype] = self.session.vreg['etypes'].etype_class(etype)


    ###########################################################################
    ### ENTITIES CREATION #####################################################
    ###########################################################################
    def get_next_eid(self):
        """ Function getting the next eid. This is done by preselecting
        a given number of eids from the 'entities_id_seq', and then
        storing them"""
        if not len(self._eids_seq):
            # We must fill the sequences
            cursor = self.session.system_sql("SELECT nextval('entities_id_seq') "
                                             "FROM generate_series(1,%(v)s);",
                                             {'v': self._eids_seq_range})
            eids = [r[0] for r in cursor.fetchall()]
            eids.reverse()
            self._eids_seq.extend(eids)
        # Pop a value
        return self._eids_seq.pop(0)

    def apply_size_constraints(self, etype, kwargs):
        """ Apply the size constraints for a given etype, attribute and value
        """
        size_constraints = self.size_constraints[etype]
        for attr, value in kwargs.items():
            if value:
                maxsize = size_constraints.get(attr)
                if maxsize is not None and len(value) > maxsize:
                    kwargs[attr] = value[:maxsize-4] + '...'
        return kwargs

    def apply_default_values(self, etype, kwargs):
        """ Apply the default values for a given etype, attribute and value
        """
        default_values = self.default_values[etype]
        for attr, value in kwargs.items():
            if value and attr not in kwargs:
                kwargs[attr] = default_values.get(attr)
        return kwargs

    def create_entity(self, etype, **kwargs):
        """ Create an entity
        """
        # Init the table if necessary
        self.init_etype_table(etype)
        # Add meta data if not given
        if 'modification_date' not in kwargs:
            kwargs['modification_date'] = self._now
        if 'creation_date' not in kwargs:
            kwargs['creation_date'] = self._now
        if 'cwuri' not in kwargs:
            if self.uri_param_name and self.uri_param_name in kwargs:
                kwargs['cwuri'] = kwargs[self.uri_param_name]
            else:
                kwargs['cwuri'] = self._default_cwuri + str(self._count_cwuri)
                self._count_cwuri += 1
        if 'eid' not in kwargs and self._eids_seq_range is not None:
            # If eid is not given and the eids sequence is set,
            # use the value from the sequence
            kwargs['eid'] = self.get_next_eid()
        # Check size constraints
        kwargs = self.apply_size_constraints(etype, kwargs)
        # Apply default values
        kwargs = self.apply_default_values(etype, kwargs)
        # Push data / Return entity
        self._data_entities[etype].append(kwargs)
        entity = self._etype_eclass_map_cache[etype](self.session)
        entity.cw_attr_cache.update(kwargs)
        if 'eid' in kwargs:
            entity.eid = kwargs['eid']
        return entity


    ###########################################################################
    ### RELATIONS CREATION ####################################################
    ###########################################################################
    def relate(self, subj_eid, rtype, obj_eid, *args, **kwargs):
        """ Compatibility with other stores
        """
        # Init the table if necessary
        self.init_relation_table(rtype)
        self._data_relations[rtype].append({'eid_from': subj_eid, 'eid_to': obj_eid})


    ###########################################################################
    ### FLUSH #################################################################
    ###########################################################################
    def on_commit(self):
        if self.on_commit_callback:
            self.on_commit_callback()

    def on_rollback(self, exc, etype, data):
        if self.on_rollback_callback:
            self.on_rollback_callback(exc, etype, data)
            self.session.rollback()
            self.session.set_cnxset()
        else:
            raise exc

    def commit(self):
        self.on_commit()
        super(MassiveObjectStore, self).commit()
        self.session.set_cnxset()

    def flush(self):
        """ Flush the data
        """
        self.flush_entities()
        self.flush_internal_relations()
        self.flush_relations()

    def flush_internal_relations(self):
        """ Flush the relations data
        """
        for rtype, data in self._data_relations.iteritems():
            if not data:
                # There is no data for these etype for this flush round.
                continue
            buf = cwdi._create_copyfrom_buffer(data, ('eid_from', 'eid_to'), replace_sep=self.replace_sep)
            if not buf:
                # The buffer is empty. This is probably due to error in _create_copyfrom_buffer
                raise ValueError
            cursor = self.session.cnxset[self.source.uri]
            # Push into the tmp table
            cursor.copy_from(buf, '%s_relation_tmp' % rtype.lower(),
                             null='NULL', columns=('eid_from', 'eid_to'))
            # Clear data cache
            self._data_relations[rtype] = []
            # Commit if asked
            if self.commit_at_flush:
                self.commit()

    def flush_entities(self):
        """ Flush the entities data
        """
        for etype, data in self._data_entities.iteritems():
            if not data:
                # There is no data for these etype for this flush round.
                continue
            # XXX It may be interresting to directly infer the columns'
            # names from the schema instead of using .keys()
            columns = data[0].keys()
            # XXX For now, the _create_copyfrom_buffer does a "row[column]"
            # which can lead to a key error.
            # Thus we should create dictionnary with all the keys.
            columns = set()
            for d in data:
                columns.update(d.keys())
            _data = []
            _base_data = dict.fromkeys(columns)
            for d in data:
                _d = _base_data.copy()
                _d.update(d)
                _data.append(_d)
            buf = cwdi._create_copyfrom_buffer(_data, columns, replace_sep=self.replace_sep)
            if not buf:
                # The buffer is empty. This is probably due to error in _create_copyfrom_buffer
                raise ValueError('Error in buffer creation for etype %s' % etype)
            columns = ['cw_%s' % attr for attr in columns]
            cursor = self.session.cnxset[self.source.uri]
            try:
                cursor.copy_from(buf, 'cw_%s' % etype.lower(), null='NULL', columns=columns)
            except Exception as exc:
                self.on_rollback(exc, etype, data)
            # Clear data cache
            self._data_entities[etype] = []
        # Flush meta data if asked
        if self.autoflush_metadata:
            self.flush_meta_data()
        # Commit if asked
        if self.commit_at_flush:
            self.commit()

    def flush_meta_data(self):
        """ Flush the meta data (entities table, is_instance table, ...)
        """
        if self.slave_mode:
            raise RuntimeError('Flushing meta data is not allow in slave mode')
        if not check_if_table_exists(self.session, 'dataio_initialized', self.pg_schema):
            self.logger.info('No information available for initialized etypes/rtypes')
            return
        if not self._metadata_table_created:
            # Keep the correctly flush meta data in database
            sql = "CREATE TABLE dataio_metadata (etype text)"
            self.session.system_sql(sql)
            self._metadata_table_created = True
        crs = self.session.system_sql('SELECT etype FROM dataio_metadata')
        already_flushed = set([e for e, in crs.fetchall()])
        crs = self.session.system_sql('SELECT retype FROM dataio_initialized WHERE type = %(t)s',
                                      {'t': 'etype'})
        all_etypes = set([e for e, in crs.fetchall()])
        for etype in all_etypes:
            if etype not in already_flushed:
                # Deals with meta data
                self.logger.info('Flushing meta data for %s' % etype)
                self.insert_massive_meta_data(etype)
                sql = 'INSERT INTO dataio_metadata VALUES (%(e)s)'
                self.session.system_sql(sql, {'e': etype})
        # Final commit
        self.commit()

    def _cleanup_entities(self, etype):
        """ Cleanup etype table """
        if self._eids_seq_range is None:
            # Remove DEFAULT eids sequence if added
            sql = 'ALTER TABLE cw_%s ALTER COLUMN cw_eid DROP DEFAULT;' % etype.lower()
            self.session.system_sql(sql)
        # Create indexes and constraints
        if self.drop_index:
            tablename = SQL_PREFIX + etype.lower()
            self.reapply_constraint_index(tablename)

    def _cleanup_relations(self, rtype):
        """ Cleanup rtype table """
        # Push into relation table while removing duplicate
        sql = '''INSERT INTO %(r)s_relation (eid_from, eid_to) SELECT DISTINCT
                 T.eid_from, T.eid_to FROM %(r)s_relation_tmp AS T
                 WHERE NOT EXISTS (SELECT 1 FROM %(r)s_relation AS TT WHERE
                 TT.eid_from=T.eid_from AND TT.eid_to=T.eid_to);''' % {'r': rtype}
        self.session.system_sql(sql)
        # Drop temporary relation table
        sql = ('DROP TABLE %(r)s_relation_tmp' % {'r': rtype.lower()})
        self.session.system_sql(sql)
        # Create indexes and constraints
        if self.drop_index:
            tablename = '%s_relation' % rtype.lower()
            self.reapply_constraint_index(tablename)

    def cleanup(self):
        """ Remove temporary tables and columns
        """
        if self.slave_mode:
            raise RuntimeError('Store cleanup is not allow in slave mode')
        self.logger.info("Start cleaning")
        # Cleanup relations tables
        super(MassiveObjectStore, self).cleanup()
        # Get all the initialized etypes/rtypes
        if check_if_table_exists(self.session, 'dataio_initialized', self.pg_schema):
            crs = self.session.system_sql('SELECT retype, type FROM dataio_initialized')
            for retype, _type in crs.fetchall():
                self.logger.info('Cleanup for %s' % retype)
                if _type == 'etype':
                    # Cleanup entities tables - Recreate indexes
                    self._cleanup_entities(retype)
                elif _type == 'rtype':
                    # Cleanup relations tables
                    self._cleanup_relations(retype)
                self.session.system_sql('DELETE FROM dataio_initialized WHERE retype = %(e)s',
                                        {'e': retype})
        # Create meta constraints (entities, is_instance_of, ...)
        self._create_metatables_constraints()
        self.commit()
        # Delete the meta data table
        for table_name in ('dataio_initialized', 'dataio_constraints', 'dataio_metadata'):
            if check_if_table_exists(self.session, table_name, self.pg_schema):
                self.session.system_sql('DROP TABLE %s' % table_name)
        self.commit()

    def insert_massive_meta_data(self, etype):
        """ Massive insertion of meta data for a given etype, based on SQL statements.
        """
        # Meta data
        self.metagen_push_relation(etype, self.session.user.eid, 'created_by_relation')
        self.metagen_push_relation(etype, self.session.user.eid, 'owned_by_relation')
        self._gen_identity_relation(etype)
        # Meta relation
        source_eid = self.session.execute('Any X WHERE X is CWSource')[0][0]
        self.metagen_push_relation(etype, source_eid, 'cw_source_relation')
        source_eid = self.session.execute('Any X WHERE X is CWEType')[0][0]
        self.metagen_push_relation(etype, source_eid, 'is_relation')
        source_eid = self.session.execute('Any X WHERE X is CWEType')[0][0]
        self.metagen_push_relation(etype, source_eid, 'is_instance_of_relation')
        # Push data - Use coalesce to avoid NULL (and get 0), if there is no
        # entities of this type in the entities table.
        sql = ("INSERT INTO entities (eid, type, source, asource, mtime, extid) "
               " SELECT cw_eid, '%s', 'system', 'system', '%s', NULL FROM cw_%s "
               "WHERE cw_eid > (SELECT coalesce(MAX(eid), 0) FROM entities WHERE type='%s')"
               % (etype, self._now, etype.lower(), etype))
        self.session.system_sql(sql)

    def _gen_identity_relation(self, etype):
        sql = ("INSERT INTO identity_relation (eid_from, eid_to) SELECT cw_eid, cw_eid FROM cw_%s "
               "WHERE cw_eid > (SELECT coalesce(MAX(eid), 0) FROM entities WHERE type='%s')"
               % (etype.lower(), etype))
        self.session.system_sql(sql)

    def metagen_push_relation(self, etype, eid_to, rtype):
        sql = ("INSERT INTO %s (eid_from, eid_to) SELECT cw_eid, %s FROM cw_%s "
               "WHERE cw_eid > (SELECT coalesce(MAX(eid), 0) FROM entities WHERE type='%s')"
               % (rtype, eid_to, etype.lower(), etype))
        self.session.system_sql(sql)


###############################################################################
###############################################################################
###############################################################################
###  !!!! WARNING !!!!  #######################################################
### This code is fow now experimental, and should be used wisely. #############
###############################################################################
###############################################################################
###############################################################################


################################################################################
### RDF STORE  #################################################################
################################################################################
class RDFStore(cwdi.NoHookRQLObjectStore, RelationStoreMixin):
    """ RDFStore is a store tjat create entities from a dictionnary of
    rdf properties.

    It should be used as following:

        store = RDFStore(session)
        ...
        store.create_entity({'http://XX': [val1, val2],
                             'http://YY': [val3, val4]})
        # Or with specifying the etype
        store.create_entity({'http://XX': [val1, val2],
                             'http://YY': [val3, val4]}, 'Person')

        # For the relations (that are not always fecthed in the
        # create_entity)
        store.relate_by_uri(uri1, 'lives', uri2)

        # Flush the relations
        store.flush()

        ...

        # Flush the relations
        store.flush()

        # Finally
        store.convert_all_relations()
        store.cleanup()
    """

    def __init__(self, session, xyreg, uri_label='cwuri',
                 internal_store=None, commit_at_flush=True, iid_maxsize=1024,
                 external_uris_dict=None):
        """ Initialize a RDFStore.
        This store create entities from a dictionnary of rdf properties.

        - xyreg is the RdfCfg object (see cubes.dataio.xy.py) that
          yields the mapping of Yams/RDF.

        - uri_label: name of the attribute of the schema used for relations convertion.

        - internal_store is an optional store used to pratically create the entities
          from the dictionnary built from the rdf properties (e.g. SQLGenObjectStore).
          If None, the create_entity is the one from the NoHookRQLObjectStore.
          WARNING: In this case, the import script is in charge of calling
          the different flush/commit method on this internal_store !

        - commit_at_flush: Boolean. Commit after each flush().

        - iid_maxsize: Int. Max size of the iid, used to create the
                       iid_eid convertion table.

        - external_uris_dict: Dict or None. Dictionnary used for storing the external uris
                              and thus avoiding multiple creations.
        """
        super(RDFStore, self).__init__(session)
        RelationStoreMixin.__init__(self, session, iid_maxsize=iid_maxsize,
                                    commit_at_flush=commit_at_flush)
        self.xyreg = xyreg
        self.xyreg.register_schema(self.session.repo.schema)
        # Additional store to be used for entity creation (possibly faster)
        self.internal_store = internal_store
        # Parameter used for relations convertion
        self.uri_label = uri_label
        # Allow to avoid the call to _init_rtype as we
        # don't know the possible destination etype
        self._initialized['relations_tuple'] = set([])
        # External uri dict for get or create
        self.external_uris = external_uris_dict if external_uris_dict is not None else {}

    def normalize_rdf_properties(self, rdf_properties):
        """ Normalize the rdf_properties predicate according to XY.
        Skip unknown predicate.
        """
        new_rdf_properties = {}
        for predicate, properties in rdf_properties.iteritems():
            predicate = normalize_xml(predicate, self.xyreg.reverse_namespaces)
            if predicate:
                # Known namespace
                new_rdf_properties[predicate] = properties
        return new_rdf_properties

    def _internal_create_entity(self, etype, entity_dict):
        """ Create an entity, using the internal store or the RDFStore
        super method """
        if self.internal_store:
            store = self.internal_store
        else:
            store = super(RDFStore, self)
        return store.create_entity(etype, **entity_dict)

    def _internal_relate(self, eid_from, rtype, eid_to):
        """ Relate, using the internal store or the RDFStore
        super method """
        if self.internal_store:
            store = self.internal_store
        else:
            store = super(RDFStore, self)
        return store.relate(eid_from, rtype, eid_to)

    def create_entity(self, rdf_properties, etype=None):
        """ Create an entity from a dictionnary of rdf properties:
        """
        #Get and normalize uri if required
        uri = rdf_properties.get(URI_RDF_PROP)
        if not uri:
            # Should exist !
            self.logger.warning('Missing URI !')
            return
        # A value of the rdf_properties dict is a list of (uri, type)
        uri = self.xyreg.normalize_uri(uri[0][0])
        # Normalize rdf properties predicates using the knwown namespaces
        rdf_properties = self.normalize_rdf_properties(rdf_properties)
        # Get etype if not given
        if not etype:
            etype = self.xyreg.guess_etype(rdf_properties)
            if not etype:
                return
        # Build entity dictionnary
        entity_dict = self.xyreg.build_entity_from_rdf(rdf_properties, etype)
        # Set the entity reference uri if needed (which may have been changed during
        # the entity dict building).
        if 'cwuri' not in entity_dict:
            entity_dict['cwuri'] = uri
        uri = entity_dict['cwuri']
        # Build the relations
        relations_data = self.build_relations_data(etype, rdf_properties)
        # Push inlined relations (do not check 1 cardinality...)
        for rtype, _eid in relations_data['inlined']:
            entity_dict[rtype] = _eid
        # Create the entity
        entity = self._internal_create_entity(etype, entity_dict)
        # Store other relations
        for rtype, _eid in relations_data['external']:
            # External relations based on eid
            self._internal_relate(entity.eid, rtype, _eid)
        for rtype, _iid in relations_data['byiid']:
            # External relations based on iid
            self.relate_by_iid(entity.eid, rtype, _iid)
        return entity

    def build_relations_data(self, etype_from, rdf_properties, normalize=False):
        """ Push the relations from rdf properties, given the uri of the subject
        and the etype_from """
        if normalize:
            # Normalize rdf properties predicates using the knwown namespaces
            rdf_properties = self.normalize_rdf_properties(rdf_properties)
        # Build the relations dictionnary from the XY mapping
        relations = self.xyreg.relations_from_rdf(rdf_properties, etype_from)
        # Push the relations
        relations_data = {'inlined': [], 'external': [], 'byiid': []}
        for rtype, rels in relations.iteritems():
            # Check if rtype is inlined or not
            inlined = self.rschema(rtype).inlined
            build_callback = self.xyreg.relations_etype_callbacks.get(rtype, None)
            for (etype_from, etype_to), uri_rels in rels.iteritems():
                # Get uri relations
                uri_rels = set([self.xyreg.normalize_uri(uri_from) for uri_from in uri_rels])
                for uri_to in uri_rels:
                    if build_callback:
                        # There exists some specific callback for relation construction
                        _etype, _edict = build_callback(uri_to)
                        sat_entity = self._internal_create_entity(_etype, _edict)
                        relation = ( rtype, sat_entity.eid)
                        if inlined:
                            relations_data['inlined'].append(relation)
                        else:
                            relations_data['external'].append(relation)
                    elif self.xyreg.is_external_uri(uri_to):
                        # Check if it is an external uri
                        exturi_eid = self.get_or_create_external_uri(uri_to)
                        relation = (rtype, exturi_eid)
                        if inlined:
                            relations_data['inlined'].append(relation)
                        else:
                            relations_data['external'].append(relation)
                    else:
                        # Simple uri-based relation
                        if (etype_from, rtype, etype_to) not in self._initialized['relations_tuple']:
                            # Initialize the table for iid relation
                            self._initialized['relations_tuple'].add((etype_from, rtype, etype_to))
                            self.init_rtype_table(etype_from, rtype, etype_to)
                        relations_data['byiid'].append(((rtype, uri_to)))
        return relations_data

    def get_or_create_external_uri(self, uri):
        """ Get or create an external uri. """
        if uri in self.external_uris:
            return self.external_uris[uri]
        # We should create it
        exturi = self._internal_create_entity('ExternalUri', {'uri': uri, 'cwuri': uri})
        self.external_uris[uri] = exturi.eid
        return exturi.eid

    def flush(self):
        """ Flush the data """
        self.flush_relations()

    def convert_all_relations(self):
        """ Convert all the relations. This will use all
        the previously seen (etype_from, rtype, etype_to) cases.
        This is useful when one don't really know which relations
        are pushed for a given set of rdf properties.
        """
        for (etype_from, rtype, etype_to) in self._initialized['relations_tuple']:
            # Relate using eid (subject) and uri (object)
            self.convert_relations(etype_from, rtype, etype_to,
                                   uri_label_from=None, uri_label_to=self.uri_label)
