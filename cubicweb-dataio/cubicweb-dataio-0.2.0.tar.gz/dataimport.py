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

from StringIO import StringIO
from datetime import datetime
from collections import defaultdict
from psycopg2 import ProgrammingError

from cubicweb.utils import make_uid
import cubicweb.dataimport as cwdi

from cubes.dataio.interfaces import URI_RDF_PROP, normalize_xml


################################################################################
### CONSTRAINTS MANAGEMENT FUNCTIONS  ##########################################
################################################################################
# Do not use cubicweb.dataimport utilities drop_indexes and create_indexes
# as we want to explicitly state which indexes are dropped (and want to
# recreate all indexes without keeping a list of these indexes
def relation_drop_constraint(session, rtype):
    sql = 'ALTER TABLE %s DROP CONSTRAINT %s_p_key' % (rtype, rtype)
    session.system_sql(sql)
    sql = 'DROP INDEX %s_to_idx' % rtype
    session.system_sql(sql)
    sql = 'DROP INDEX %s_from_idx' % rtype
    session.system_sql(sql)

def relation_create_constraint(session, rtype):
    sql = 'ALTER TABLE %s ADD PRIMARY KEY (eid_from, eid_to)' % rtype
    session.system_sql(sql)
    sql = 'ALTER INDEX %s_pkey RENAME TO %s_p_key' % (rtype, rtype)
    session.system_sql(sql)
    sql = 'CREATE INDEX %s_to_idx ON %s (eid_to)' % (rtype, rtype)
    session.system_sql(sql)
    sql = 'CREATE INDEX %s_from_idx ON %s (eid_from)' % (rtype, rtype)
    session.system_sql(sql)


################################################################################
### RELATION STORE MIXIN #######################################################
################################################################################
class RelationStoreMixin(object):
    """ Mixin for stores to implement the behavior of relation
    based on external id (e.g. uri)
    """

    def __init__(self, session, replace_sep=None,
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
        self.session = session
        self.iid_maxsize = iid_maxsize
        self.replace_sep = replace_sep
        self.commit_at_flush = commit_at_flush
        self._data_relations = defaultdict(list)
        self._initialized = {'init_uri_eid': set([]),
                             'uri_eid_inserted': set([]),
                             'relations': set([])}

    def init_rtype_table(self, etype_from, rtype, etype_to):
        """ Build temporary table a for standard rtype """
        # Create an uri_eid table for each etype for a better
        # control of which etype is concerns for a particular
        # possibly multivalued relation.
        for etype in (etype_from, etype_to):
            if etype not in self._initialized['init_uri_eid']:
                self._init_uri_eid_table(etype)
        if rtype not in self._initialized['relations']:
            # Create the temporary tables
            if not self.rschema(rtype).inlined:
                try:
                    sql = 'CREATE TABLE %(r)s_relation_tmp (uri_from character ' \
                          'varying(%(s)s), uri_to character varying(%(s)s))'
                    self.session.system_sql(sql % {'r': rtype, 's': self.iid_maxsize})
                except ProgrammingError:
                    # XXX Already exist (probably due to multiple import)
                    pass
            else:
                print ("inlined relation %s: cannot insert it" % rtype)
            #Add it to the initialized set
            self._initialized['relations'].add(rtype)

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

    def flush_relations(self):
        """ Flush the relations data
        """
        for rtype, data in self._data_relations.iteritems():
            if not data:
                print 'No data for rtype', rtype
                continue
            buf = StringIO('\n'.join(['%(uri_from)s\t%(uri_to)s' % d for d in data]))
            if not buf:
                print 'Empty Buffer for rtype', rtype
                continue

            cursor = self.session.cnxset[self.source.uri]
            if not self.rschema(rtype).inlined:
                cursor.copy_from(buf, '%s_relation_tmp' % rtype.lower(), null='NULL', columns=('uri_from', 'uri_to'))
            else:
                print ("inlined relation %s: cannot insert it" % rtype)
            buf.close()
            # Clear data cache
            self._data_relations[rtype] = []
            # Commit if asked
            if self.commit_at_flush:
                self.commit()

    def cleanup(self):
        """ Remove temporary tables and columns
        """
        print "Start cleaning"
        # Cleanup tables
        for etype in self._initialized['init_uri_eid']:
            self.session.system_sql('DROP TABLE uri_eid_%s' % etype.lower())
        # Remove relations tables
        for rtype in self._initialized['relations']:
            if not self.rschema(rtype).inlined:
                self.session.system_sql('DROP TABLE %(r)s_relation_tmp' % {'r': rtype})
            else:
                print ("inlined relation %s: no cleanup to be done for it" % rtype)
        self.commit()

    def fill_uri_eid_table(self, etype, uri_label):
        """ Fill the uri_eid table
        """
        print 'Fill uri_eid for etype', etype
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
        print 'Flush relations'
        self.flush_relations()
        if etype_from not in self._initialized['uri_eid_inserted']:
            self.fill_uri_eid_table(etype_from, uri_label_from)
        if etype_to not in self._initialized['uri_eid_inserted']:
            self.fill_uri_eid_table(etype_to, uri_label_to)
        sql = '''INSERT INTO %(r)s_relation (eid_from, eid_to) SELECT DISTINCT O1.eid, O2.eid
        FROM %(r)s_relation_tmp AS T, uri_eid_%(ef)s as O1, uri_eid_%(et)s as O2
        WHERE O1.uri=T.uri_from AND O2.uri=T.uri_to AND NOT EXISTS (
        SELECT 1 FROM %(r)s_relation AS TT WHERE TT.eid_from=O1.eid AND TT.eid_to=O2.eid);
        '''
        try:
            if not self.rschema(rtype).inlined:
                self.session.system_sql(sql % {'r': rtype.lower(),
                                               'et': etype_to.lower(),
                                               'ef': etype_from.lower(),
                                               })
            else:
                print ("inlined relation %s: cannot insert it" % rtype)
        except Exception as ex:
            print "Cannot insert relation %s: %s" % (rtype, ex)
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
                 replace_sep=None, commit_at_flush=True,
                 iid_maxsize=1024, uri_param_name='rdf:about', build_entities=False):
        """ Create a MassiveObject store, with the following attributes:

        - session: CubicWeb session
        - autoflush_metadata: Boolean.
                              Automatically flush the metadata after
                              each flush()
        - replace_sep: String. Replace separator used for
                       (COPY FROM) buffer creation.
        - commit_at_flush: Boolean. Commit after each flush().
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
        self.autoflush_metadata = autoflush_metadata
        self.replace_sep = replace_sep
        self._build_entities = build_entities
        self._data_entities = defaultdict(list)
        self._etype_eclass_map_cache = {}
        self.indexes_etypes = defaultdict(list)
        self._now = datetime.now()
        self._default_cwuri = make_uid('_auto_generated')
        self.uri_param_name = uri_param_name
        self._count_cwuri = 0
        self.commit_at_flush = commit_at_flush
        self._drop_constraints() # recreate then when self.cleanup() is called
        self._initialized['entities'] = set([])


    ###########################################################################
    ### SQL UTILITIES #########################################################
    ###########################################################################
    def _drop_constraints(self):
        """ Drop all the constraints for the meta data"""
        sql = 'ALTER TABLE entities DROP CONSTRAINT entities_pkey'
        self.session.system_sql(sql)
        sql = 'DROP INDEX entities_extid_idx'
        self.session.system_sql(sql)
        sql = 'DROP INDEX entities_mtime_idx'
        self.session.system_sql(sql)
        sql = 'DROP INDEX entities_type_idx'
        self.session.system_sql(sql)
        relation_drop_constraint(self.session, 'created_by_relation')
        relation_drop_constraint(self.session, 'owned_by_relation')
        relation_drop_constraint(self.session, 'is_instance_of_relation')
        relation_drop_constraint(self.session, 'identity_relation')

    def _create_constraints(self):
        """ Create all the constraints for the meta data"""
        sql = 'ALTER TABLE entities ADD PRIMARY KEY (eid)'
        self.session.system_sql(sql)
        sql = 'CREATE INDEX entities_extid_idx ON entities (extid)'
        self.session.system_sql(sql)
        sql = 'CREATE INDEX entities_mtime_idx ON entities (mtime)'
        self.session.system_sql(sql)
        sql = 'CREATE INDEX entities_type_idx ON entities (type)'
        self.session.system_sql(sql)
        relation_create_constraint(self.session, 'created_by_relation')
        relation_create_constraint(self.session, 'owned_by_relation')
        relation_create_constraint(self.session, 'is_instance_of_relation')
        relation_create_constraint(self.session, 'identity_relation')

    def init_etype_table(self, etype):
        """ Add eid sequence to a particular etype table """
        sql = ("ALTER TABLE cw_%s ALTER COLUMN cw_eid "
               "SET DEFAULT nextval('entities_id_seq')" % etype.lower())
        self.session.system_sql(sql)
        # Get and remove all indexes for performance sake
        for name, attr in self.iterate_application_indexes(etype):
            self.indexes_etypes[etype].append((name, attr))
            sql = 'DROP INDEX %s' % name
            self.session.system_sql(sql)
        self._initialized['entities'].add(etype)
        # Add the etype class to the cache
        self._etype_eclass_map_cache[etype] = self.session.vreg['etypes'].etype_class(etype)

    def iterate_application_indexes(self, etype):
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
        AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
        AND pg_catalog.pg_table_is_visible(c.oid)
        ORDER BY 1,2;'''
        indexes = self.session.system_sql(sql).fetchall()
        for name, type, table in indexes:
            # Do not consider 'cw_etype_pkey' index
            if (type == 'index' and table == 'cw_%s' % etype.lower()
                and not name.endswith('key')):
                attr = name.replace(table, '', 1).replace('idx', '', 1).strip('_')
                yield name, attr


    ###########################################################################
    ### ENTITIES CREATION #####################################################
    ###########################################################################
    def create_entity(self, etype, **kwargs):
        """ Create an entity
        """
        # Init the table if necessary
        if etype not in self._initialized['entities']:
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
        # Push data
        self._data_entities[etype].append(kwargs)
        if self._build_entities:
            entity = self._etype_eclass_map_cache[etype](kwargs)
            entity.cw_attr_cache.update(kwargs)
            return entity


    ###########################################################################
    ### RELATIONS CREATION ####################################################
    ###########################################################################
    # Do not add this function to the RelationStoreMixin as the name
    # could actually change for refleting a bussiness aspect.
    def relate_by_iid(self, iid_from, rtype, iid_to):
        """Add new relation based on the internal id (iid)
        of the entities (not the eid)"""
        # Push data
        if isinstance(iid_from, unicode):
            iid_from = iid_from.encode('utf-8')
        else:
            print ("'iid_from' format is %s; Unicode expected"
                   % type(iid_from).__name__)
        if isinstance(iid_to, unicode):
            iid_to = iid_to.encode('utf-8')
        else:
            print ("'iid_to' format is %s; Unicode expected"
                   % type(iid_to).__name__)
        self._data_relations[rtype].append({'uri_from': iid_from, 'uri_to': iid_to})


    ###########################################################################
    ### FLUSH #################################################################
    ###########################################################################
    def flush(self):
        """ Flush the data
        """
        self.flush_entities()
        self.flush_relations()

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
            buf = cwdi._create_copyfrom_buffer(data, columns, replace_sep=self.replace_sep)
            if not buf:
                # The buffer is empty. This is probably due to error in _create_copyfrom_buffer
                raise ValueError
            columns = ['cw_%s' % attr for attr in columns]
            cursor = self.session.cnxset[self.source.uri]
            cursor.copy_from(buf, 'cw_%s' % etype.lower(), null='NULL', columns=columns)
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
        for etype in self._data_entities:
            # Deals with meta data
            self.insert_massive_meta_data(etype)
        # Final commit
        self.commit()

    def cleanup(self):
        """ Remove temporary tables and columns
        """
        print "Start cleaning"
        # Cleanup relations tables
        super(MassiveObjectStore, self).cleanup()
        # Cleanup entities tables
        for etype in self._initialized['entities']:
            # Remove DEFAULT sequence
            sql = 'ALTER TABLE cw_%s ALTER COLUMN cw_eid DROP DEFAULT;' % etype.lower()
            self.session.system_sql(sql)
            # Recreate indexes
            for name, attr in self.indexes_etypes[etype]:
                sql = 'CREATE INDEX %s ON cw_%s (%s)' % (name, etype.lower(), attr)
                self.session.system_sql(sql)
        # Create constraints
        self._create_constraints()
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

    def create_entity(self, rdf_properties, etype=None):
        """ Create an entity from a dictionnary of rdf properties:

        """
        #Get and normalize uri if required
        uri = rdf_properties.get(URI_RDF_PROP)
        if not uri:
            # Should exist !
            print 'Missing URI !'
            return
        # A value of the rdf_properties dict is a list of (uri, type)
        uri = self.xyreg.normalize_uri(uri[0][0])
        # Normalize rdf properties predicates using the knwown namespaces
        rdf_properties = self.normalize_rdf_properties(rdf_properties)
        # Get etype if not given
        if not etype:
            etype = self.xyreg.guess_etype(rdf_properties)
            if not etype:
                #print 'Could not handle these rdf properties, no matching etype !'
                return
        # Build entity dictionnary
        entity_dict = self.xyreg.build_entity_from_rdf(rdf_properties, etype)
        # Set the entity reference uri if needed (which may have been changed during
        # the entity dict building).
        if 'cwuri' not in entity_dict:
            entity_dict['cwuri'] = uri
        uri = entity_dict['cwuri']
        # Create inlined relations - Not used for now
        ## inlined_relations = self.build_inlined_relations(rdf_properties, etype)
        # Build and store the relations
        self.push_relations(uri, etype, rdf_properties)
        # Create the entity
        if self.internal_store:
            # Use the given internal_store
            return self.internal_store.create_entity(etype, **entity_dict)
        return super(RDFStore, self).create_entity(etype, **entity_dict)

    def relate_by_uri(self, uri_from, rtype, uri_to):
        """Add new relation based on the uris of the entities (not the eid)"""
        self._data_relations[rtype].append({'uri_from': uri_from, 'uri_to': uri_to})

    def push_relations(self, uri, etype_from, rdf_properties, normalize=False):
        """ Push the relations from rdf properties, given the uri of the subject
        and the etype_from """
        if normalize:
            # Normalize rdf properties predicates using the knwown namespaces
            rdf_properties = self.normalize_rdf_properties(rdf_properties)
        # Build the relations dictionnary from the XY mapping
        relations = self.xyreg.relations_from_rdf(rdf_properties, etype_from)
        # Push the relations
        for rtype, rels in relations.iteritems():
            for (etype_from, etype_to), uri_rels in rels.iteritems():
                ## # Initialize the tables
                if (etype_from, rtype, etype_to) not in self._initialized['relations_tuple']:
                    self._initialized['relations_tuple'].add((etype_from, rtype, etype_to))
                    self.init_rtype_table(etype_from, rtype, etype_to)
                # Store the relations
                uri_rels = set([self.xyreg.normalize_uri(uri_from) for uri_from in uri_rels])
                for uri_to in uri_rels:
                    # Check if it is an external uri
                    if self.xyreg.is_external_uri(uri_to):
                        # This is an external uri
                        exturi_eid = self.get_or_create_external_uri(uri_to)
                    self.relate_by_uri(uri, rtype, uri_to)

    def get_or_create_external_uri(self, uri):
        """ Get or create an external uri. """
        if uri in self.external_uris:
            return self.external_uris[uri]
        # We should create it
        if self.internal_store:
            exuri = self.internal_store.create_entity('ExternalUri', uri=uri, cwuri=uri)
        else:
            exuri = self.create_entity('ExternalUri', uri=uri, cwuri=uri)
        self.external_uris[uri] = exuri.eid
        return exuri.eid

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
            self.convert_relations(etype_from, rtype, etype_to,
                                   self.uri_label, self.uri_label)
