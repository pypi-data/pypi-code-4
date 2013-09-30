#!/usr/bin/python

"""
Defines the base connection class that will be used for communication
to the backend databases.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

# not using undefined variables is ok for abstract classes
# pylint: disable-msg=W0613

import cPickle
import datetime
import glob
import os.path
import logging
import random

from xml.etree import ElementTree

import projex
import projex.rest
import projex.text
from projex.decorators import abstractmethod

import orb

from orb import errors
from orb import settings
from orb import backends
from orb.common import ColumnType
from orb.query import Query, QueryCompound

logger = logging.getLogger(__name__)

MAX_INT = 2**64-1

try:
    import pytz
except ImportError:
    pytz = None

#----------------------------------------------------------------------

class CommandEngine(object):
    """ Defines a class for generating SQL statments for a table """
    def __init__(self, backend, wrapper='`'):
        self._backend = backend
        self._commands = {}
        self._stringWrapper = wrapper
    
    def backend(self):
        """
        Returns the backend associated with this engine.
        
        :return     <orb.Connection>
        """
        return self._backend
    
    def command(self, key):
        """
        Returns the SQL command for the given key.
        
        :param      key | <variant>
        
        :return     <str> | command
        """
        return self._commands.get(key, '').strip()
    
    def genkey(self, key):
        """
        Generates a random key for the key in the data dictionary
        for the inputed key.
        
        :param      key | <str>
        """
        return '{0}-{1:x}-{2:x}'.format(key,
                                        random.randint(0, MAX_INT),
                                        random.randint(0, MAX_INT))
    
    def setCommand(self, key, command):
        """
        Sets the sql command for the given key to the inputed command.
        
        :param      key     | <variant>
                    command | <str>
        """
        self._commands[key] = command

    def setStringWrapper(self, wrapper):
        """
        Sets the string wrapper for this command engine.
        
        :param      wrapper | <str>
        """
        self._stringWrapper = wrapper

    def stringWrapper(self):
        """
        Returns the string wrapper for this command engine.
        
        :return     <str>
        """
        return self._stringWrapper
    
    def wrapString(self, *args, **kwds):
        """
        Wraps the protected text in a database specific way.  This will ensure
        the given text is treated as a particular name in the DB vs. a possible
        keyword that would cause a query error.
        
        :param      text | <str>
        
        :return     <str>
        """
        sep = kwds.get('separator', '.')
        ch = self.stringWrapper()
        return sep.join(map(lambda x: ch + x + ch, args))

#----------------------------------------------------------------------

class ColumnEngine(CommandEngine):
    def addCommand(self, column):
        """
        Returns the command used for adding this column to a table.
        
        :return     <str>
        """
        return ''
    
    def createCommand(self, column):
        """
        Returns the creation command for this column.
        
        :return     <str>
        """
        return ''
    
    def queryCommand(self,
                     column,
                     op,
                     value,
                     offset='',
                     caseSensitive=False,
                     setup=None):
        """
        Converts the inputed column, operator and value to a query statement.
        
        :param      columns       | <orb.TableSchema>
                    op            | <orb.Column.Op>
                    value         | <variant>
                    caseSensitive | <bool>
        
        :return     <str> cmd, <dict> data
        """
        return '', {}
    
    def fromString(self, value_str):
        """
        Converts the inputed string to a value for this engine.
        
        :param      value_str | <str>
        
        :return     <variant>
        """
        try:
            return eval(value_str)
        except:
            return value_str
    
    def toString(self, value):
        """
        Converts the inputed value to a string representation.
        
        :param      value | <variant>
        
        :return     <str>
        """
        return str(value)
    
    def unwrap(self, column, value):
        """
        Unwraps the inputed value from the database to the proper Python value.
        
        :param      value | <variant>
        """
        coltype = ColumnType.base(column.columnType())
        
        if coltype == ColumnType.Pickle:
            try:
                return cPickle.loads(str(value))
            except:
                return None
        
        elif coltype in (ColumnType.String, 
                         ColumnType.Email, 
                         ColumnType.Password,
                         ColumnType.Filepath,
                         ColumnType.Url,
                         ColumnType.Text,
                         ColumnType.Xml):
            if value is not None:
                return projex.text.encoded(value, column.encoding())
        
        elif coltype == ColumnType.Dict:
            return projex.rest.dejsonify(value)
        
        return value
    
    def wrap(self, column, value):
        """
        Converts the inputed value to be able to be stored in the database.
        
        :param      value | <variant>
        """
        coltype = ColumnType.base(column.columnType())
        
        # convert a pickle value
        if coltype == ColumnType.Pickle:
            return cPickle.dumps(value)
        
        # lookup records set values
        elif orb.RecordSet.typecheck(value):
            return value.primaryKeys()
        
        # lookup a record
        elif orb.Table.recordcheck(value):
            nvalue = value.primaryKey()
            if not nvalue:
                return None
            return nvalue
        
        # convert list/tuple information to clean values
        elif type(value) in (list, tuple, set):
            return tuple(map(lambda x: self.wrap(column, x), value))
        
        # convert timedelta information
        elif type(value) == datetime.timedelta:
            now = datetime.datetime.now()
            dtime = now + value
            return self.wrap(column, dtime)
        
        # convert timezone information
        elif type(value) == datetime.datetime:
            # convert timezone information to UTC data
            if value.tzinfo is not None and pytz:
                return value.astimezone(pytz.utc).replace(tzinfo=None)
            return value
        
        # convert dictionary data to database
        elif type(value) == dict:
            return projex.rest.jsonify(value)
        
        # convert string information
        elif column is not None and coltype in (ColumnType.String,
                                                ColumnType.Text):
            return projex.text.encoded(value, column.encoding())
        
        return value

#----------------------------------------------------------------------

class SchemaEngine(CommandEngine):
    def alterCommand(self, schema, columns=None):
        """
        Generates the alter table command.
        
        :param      schema | <orb.TableSchema>
                    db     | <orb.Database> || None
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def columnsCommand(self, schema):
        """
        Returns the command for the inputed schema to lookup its
        columns from the database.
        
        :return     <str>, <dict>
        """
        return '', {}
    
    def countCommand(self, schemas, **options):
        """
        Returns the command that will be used to calculate the count that
        will be returned for the given query options.
        
        :param      schemas   | [<orb.TableSchema>, ..]
                    **options | database options
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def createCommand(self, schema):
        """
        Generates the table creation command.
        
        :param      schema | <orb.TableSchema>
                    db     | <orb.Database> || None
                    
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def deleteCommand(self, schema, records):
        """
        Generates the table deletion command.
        
        :param      schema  | <orb.TableSchema>
                    records | [<variant> pkey, ..]
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def disableInternalsCommand(self, schema):
        """
        Generates the disable internals command for this schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def enableInternalsCommand(self, schema):
        """
        Generates the enable internals command for this schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def existsCommand(self, schema):
        """
        Returns the command that will determine whether or not the schema
        exists in the database.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> command, <dict> data
        """
        return '', {}
    
    def insertCommand(self, schema, records, columns=None):
        """
        Generates the table insertion command.
        
        :param      schema  | <orb.TableSchema>
                    records | [<orb.Table>, ..]
                    columns | [<str>, ..] || None
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def queryCommand(self, schemas, query, setup=None):
        """
        Generates the query command for the given information.
        
        :param      schemas | <orb.TableSchema>
                    query   | <orb.Query>
                    setup   | <dict> || None
        
        :return     <str> command, <dict> data
        """
        return '', {}
    
    def queryCompoundCommand(self, schemas, query, setup=None):
        """
        Generates the query compound command for the given information.
        
        :param      schemas | <orb.TableSchema>
                    query   | <orb.QueryCompound>
                    setup   | <dict> || None
        
        :return     <str> command, <dict> data
        """
        where_commands = []
        having_commands = []
        data = {}
        
        for q in query.queries():
            where_command, having_command, qdata = self.whereCommand(schemas,
                                                                     q,
                                                                     setup)
            
            if where_command:
                where_commands.append(where_command)
            if having_command:
                having_commands.append(having_command)
            
            if where_command or having_command:
                data.update(qdata)
        
        optype  = query.operatorType()
        strtype = orb.QueryCompound.Op[optype].upper()
        joiner  = ' {0} '.format(strtype)
        
        if where_commands:
            where_command = '({0})'.format(joiner.join(where_commands))
        else:
            where_command = ''
        
        if having_commands:
            having_command = '({0})'.format(joiner.join(having_commands))
        else:
            having_command = ''
        
        if not (having_command or where_command):
            data = {}
        
        return where_command, having_command, data
    
    def queryOffset(self, schemas, query, setup=None):
        """
        Generates the offset query information
        """
        typ   = query.offsetType()
        value = query.offsetValue()
        
        # generate the offset value query
        if Query.typecheck(value):
            value_str, data = self.queryValue(schemas, value, setup)
        else:
            column = query.column(schemas[0])
            engine = column.engine(self.backend().database())
            if engine:
                value = engine.wrap(column, value)
            
            key = self.genkey('offset')
            data = {key: value}
            value_str = '%({0})s'.format(key)
        
        symbol = Query.OffsetSymbol.get(typ)
        if symbol:
            return (symbol + value_str, data)
        else:
            return ('', {})
    
    def queryValue(self, schemas, query, setup=None):
        """
        Converts a query to the database lookup value.
        
        :param      schemas | [<orb.TableSchema>, ..]
                    query   | <orb.Query>
                    setup   | <dict> || None
        
        :return     (<str> command, <dict> data)
        """
        column = query.column(schemas[0])
        if not column:
            raise errors.ColumnNotFoundWarning(query.columnName())
        
        if self.backend().isObjectOriented():
            schema = column.firstMemberSchema(schemas)
        else:
            schema = column.schema()
        
        cmd = self.wrapString(schema.tableName(), column.fieldName())
        if query.isOffset():
            offset, data = self.queryOffset(schemas, query, setup)
            cmd += offset
        else:
            data = {}
        
        return cmd, data
        
    def removeCommand(self, schema, records):
        """
        Generates the command for removing the inputed records from the
        database.
        
        :param      schema  | <orb.TableSchema>
                    records | [<orb.Table>, ..]
        
        :return     <str> command, <dict> data
        """
        return '', {}
        
    def selectCommand(self, schemas, **options):
        """
        Generates the command that will be used when selecting records from
        the database.
        
        :param      schemas | [<orb.TableSchema>, ..]
                    **options | query options
        
        :return     <str> sql, <dict> data
        """
        return '', {}
    
    def updateCommand(self, schema, records, columns=None):
        """
        Generates the command that will be used when updating records within
        the database.
        
        :param      schema | <orb.TableSchema>
                    records | [<orb.Table>, ..]
                    columns | [<str>, ..] || None
        
        :return     <str> sql, <dict> data
        """
        return '', {}

    def whereCommand(self, schemas, where, setup=None):
        """
        Generates the query command for the given information.
        
        :param      schemas | <orb.TableSchema>
                    where   | <orb.Query> || <orb.QueryCompound>
                    setup   | <dict> || None
        
        :return     <str> where_command, <str> having_command, <dict> data
        """
        # generate sub-query options
        if orb.QueryCompound.typecheck(where):
            return self.queryCompoundCommand(schemas, where, setup)
        elif where:
            column = where.column(schemas[0])
            cmd, data = self.queryCommand(schemas, where, setup)
            
            if column is not None and column.isAggregate():
                return '', cmd, data
            else:
                return cmd, '', data
        else:
            return '', '', {}
    
#----------------------------------------------------------------------

class DatabaseOptions(object):
    """"
    Defines a unique instance of information that will be bundled when
    calling different methods within the connections class.
    """
    def __init__( self, **kwds ):
        throwErrors = settings.RAISE_BACKEND_ERRORS == 'True'
        self.defaults = {'namespace': None,
                         'flags': 0,
                         'dryRun': False,
                         'useCache': False,
                         'inflateRecords': True,
                         'throwErrors': throwErrors}
        
        self.namespace          = kwds.get('namespace')
        self.flags              = kwds.get('flags', 0)
        self.dryRun             = kwds.get('dryRun', False)
        self.useCache           = kwds.get('useCache', False)
        self.inflateRecords     = kwds.get('inflated', 
                                  kwds.get('inflateRecords', True))
        self.throwErrors        = kwds.get('throwErrors', throwErrors)
    
    def __str__(self):
        """
        Returns a string for this instance.
        
        :return     <str>
        """
        opts = []
        for key, default in self.defaults.items():
            val = getattr(self, key)
            if val == default:
                continue
            
            opts.append('{0}:{1}'.format(key, val))
        
        return '<DatabaseOptions {0}>'.format(' '.join(opts))
    
    def __hash__(self):
        """
        Returns a hash representation for this instance.
        
        :return     <hash>
        """
        return hash(str(self))
    
    def isNull(self):
        """
        Returns whether or not this option set has been modified.
        
        :return     <bool>
        """
        for key, default in self.defaults.items():
            val = getattr(self, key)
            if val != default:
                return False
        return True
    
    def toDict(self):
        """
        Returns a dictionary representation of this database option set.
        
        :return     <dict>
        """
        out = {}
        out['namespace']        = self.namespace
        out['flags']            = self.flags
        out['dryRun']           = self.dryRun
        out['useCache']         = self.useCache
        out['inflateRecords']   = self.inflateRecords
        out['throwErrors']      = self.throwErrors
        return out
    
    @staticmethod
    def fromDict(data):
        """
        Returns a new lookup options instance based on the inputed data
        dictionary.
        
        :param      data | <dict>
        
        
        :return     <LookupOptions>
        """
        return DatabaseOptions(**data)

#------------------------------------------------------------------------------

class LookupOptions(object):
    """
    Defines a unique instance of information that will be bundled when
    calling different query based methods in the connection class.
    """
    def __init__(self, **kwds):
        self.columns  = kwds.get('columns', None)
        self.where    = kwds.get('where',   None)
        self.order    = kwds.get('order',   None)
        self.start    = kwds.get('start',   None)
        self.limit    = kwds.get('limit',   None)
        self.distinct = kwds.get('distinct', False)
    
    def __str__(self):
        """
        Returns a string for this instance.
        
        :return     <str>
        """
        opts = []
        for key in ('columns', 'where', 'order', 'start', 'limit'):
            val = getattr(self, key)
            if val is None:
                continue
            
            if Query.typecheck(val) or QueryCompound.typecheck(val):
                val = hash(val.toXmlString())
            
            opts.append('{0}:{1}'.format(key, val))
        
        if self.distinct:
            opts.append('distinct:True')
        
        return '<LookupOptions {0}>'.format(' '.join(opts))
    
    def __hash__(self):
        """
        Returns a hash representation for this instance.
        
        :return     <hash>
        """
        return hash(str(self))
    
    def isNull(self):
        """
        Returns whether or not this lookup option is NULL.
        
        :return     <bool>
        """
        for key in ('columns', 'where', 'order', 'start', 'limit', 'distinct'):
            if getattr(self, key):
                return False
        return True
    
    def toDict(self):
        """
        Returns a dictionary representation of the lookup options.
        
        :return     <dict>
        """
        out = {}
        if self.columns:
            out['columns'] = self.columns[:]
        if self.where:
            out['where'] = self.where.toDict()
        if self.order:
            out['order'] = self.order[:]
        if self.start:
            out['start'] = self.start
        if self.limit:
            out['limit'] = self.limit
        
        return out
    
    @staticmethod
    def fromDict(data):
        """
        Returns a new lookup options instance based on the inputed data
        dictionary.
        
        :param      data | <dict>
        
        
        :return     <LookupOptions>
        """
        from orb import Query
        
        kwds = {}
        kwds.update(data)
        if 'where' in data:
            kwds['where'] = Query.fromDict(data['where'])
        
        return LookupOptions(**kwds)

#------------------------------------------------------------------------------

class Connection(object):
    """ 
    Defines the base connection class type.  This class is used to handle
    database transactions and queries.  The Connection class needs to be
    subclassed to handle connection to a particular kind of database backend,
    the backends that are included with the orb package can be found in the
    orb.backends package.
    """
    backends = {}
    
    # define the options class that will be used for backend information
    DatabaseOptionsClass = DatabaseOptions
    LookupOptionsClass   = LookupOptions
    
    def __init__(self, database):
        self._database          = database
        self._threadEnabled     = False
        self._internalsEnabled  = True
        self._commitEnabled     = True
        self._engine            = None
        self._columnEngines     = {}
    
    def __del__(self):
        """
        Closes the connection when the connection instance is deleted.
        """
        self.close()
    
    def backup(self, filename, **options):
        """
        Backs up the data from this database backend to the inputed filename.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        data = {}
        for schema in self.database().schemas():
            colnames = schema.columnNames(recurse=self.isObjectOriented(),
                                          includeProxies=False,
                                          includeJoined=False,
                                          includeAggregates=False)
            
            values = schema.model().select(colnames, inflated=False).all()
            data[schema.name()] = map(lambda x: dict(zip(colnames, x)), values)
        
        # save this backup to the database file
        f = open(filename, 'wb')
        cPickle.dump(data, f)
        f.close()
    
    @abstractmethod()
    def close( self ):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        return True
    
    @abstractmethod()
    def commit( self ):
        """
        Commits the changes to the current database connection.
        
        :return     <bool> success
        """
        return False
    
    def commitEnabled(self):
        """
        Returns whether or not committing is currently enabled.
        
        :return     <bool>
        """
        return self._commitEnabled and self.internalsEnabled()
    
    @abstractmethod()
    def count( self, table_or_join, lookup, options ):
        """
        Returns the number of records that exist for this connection for
        a given lookup and options.
        
        :sa         distinct, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     <int>
        """
        return 0
    
    @abstractmethod()
    def createTable( self, schema, options ):
        """
        Creates a new table in the database based cff the inputed
        table information.
        
        :param      schema   | <orb.TableSchema>
                    options  | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        return False
    
    def columnEngine(self, columnType):
        """
        Returns the data engine associated with this backend for the given
        column type.
        
        :param      columnType | <orb.ColumnType>
        """
        return self._columnEngines.get(columnType)
    
    def columnEngines(self):
        """
        Returns a dict of the column engines associated with this connection.
        
        :return     {<orb.ColumnType> coltype: <orb.ColumnEngine>, ..}
        """
        return self._columnEngines
    
    def database(self):
        """
        Returns the database instance that this connection is
        connected to.
        
        :return     <Database>
        """
        return self._database
    
    def defaultPrimaryColumn( self ):
        """
        Defines a default column to be used as the primary column for this \
        database connection.  By default, an auto-incrementing integer field \
        called '_id' will be defined.
        
        :return     <orb.Column>
        """
        from orb import Column, ColumnType
        return Column(ColumnType.Integer,
                      settings.PRIMARY_FIELD,
                      primary          = True,
                      autoIncrement    = True,
                      fieldName        = settings.PRIMARY_FIELD,
                      getterName       = settings.PRIMARY_GETTER,
                      setterName       = settings.PRIMARY_SETTER,
                      displayName      = settings.PRIMARY_DISPLAY,
                      indexName        = settings.PRIMARY_INDEX,
                      indexed          = True,
                      unique           = True,
                      readOnly         = True,
                      private          = True)
    
    def defaultInheritColumn(self, schema):
        """
        Defines a default column to be used as the primary column for this \
        database connection.  By default, an auto-incrementing integer field \
        called '_id' will be defined.
        
        :return     <orb.Column>
        """
        from orb import Column, ColumnType
        col = Column(ColumnType.ForeignKey,
                      settings.INHERIT_FIELD,
                      fieldName        = settings.INHERIT_FIELD,
                      unique           = True,
                      private          = True)
        
        col.setReference(schema.inherits())
        col._schema = schema
        
        return col
    
    def disableInternals(self):
        """
        Disables the internal checks and update system.  This method should
        be used at your own risk, as it will ignore errors and internal checks
        like auto-incrementation.  This should be used in conjunction with
        the enableInternals method, usually these are used when doing a
        bulk import of data.
        
        :sa     enableInternals
        """
        self._internalsEnabled = False
    
    @abstractmethod()
    def distinct( self, table_or_join, lookup, options ):
        """
        Returns the distinct set of records that exist for a given lookup
        for the inputed table or join instance.
        
        :sa         count, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        return 0
        
    def enableInternals(self):
        """
        Enables the internal checks and update system.  This method should
        be used at your own risk, as it will ignore errors and internal checks
        like auto-incrementation.  This should be used in conjunction with
        the disableInternals method, usually these are used when doing a
        bulk import of data.
        
        :sa     disableInternals
        """
        self._internalsEnabled = True
        
    def engine(self):
        """
        Returns the engine associated with this connection backend.
        
        :return     <orb.SchemaEngine>
        """
        return self._engine
    
    @abstractmethod()
    def execute( self, command, data=None, flags=0):
        """
        Executes the inputed command into the current 
        connection cursor.
        
        :param      command  | <str>
                    data     | <dict> || None
                    flags    | <orb.DatabaseFlags>
        
        :return     <variant> returns a native set of information
        """
        return None
    
    @abstractmethod()
    def insert(self, record, lookup, options):
        """
        Inserts the database record into the database with the
        given values.
        
        :param      record      | <orb.Table>
                    lookup      | <orb.LookupOptions>
                    options     | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    def internalsEnabled(self):
        """
        Returns whether or not this connection has its internal checks and
        optimizations enabled or not.
        
        :sa         disableInternals, enableInternals
        
        :return     <bool>
        """
        return self._internalsEnabled
    
    def interrupt(self, threadId=None):
        """
        Interrupts/stops the database access through a particular thread.
        
        :param      threadId | <int> || None
        """
        pass
    
    @abstractmethod()
    def isConnected( self ):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return False
    
    def isThreadEnabled( self ):
        """
        Returns whether or not this connection can be threaded.
        
        :return     <bool>
        """
        return self._threadEnabled
    
    @abstractmethod()
    def open( self ):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        return False
    
    def remove(self, schema, records, options):
        """
        Removes the inputed records from the database.
        
        :param      schema      | <orb.TableSchema>
                    records     | [<orb.Table> record, ..] || <orb.RecordSet>
                    options     | <orb.DatabaseOptions>
        
        :return     <int> number of rows removed
        """
         # group the records by their schemas
        schema_keys = {}
        removing    = []
        for record in records:
            if orb.Table.recordcheck(record):
                key_schema = record.schema()
                key = record.primaryKey()
            else:
                key_schema = schema
                key = record
            
            if not key:
                continue
            
            removing.append(record)
            schema_keys.setdefault(key_schema, [])
            schema_keys[key_schema].append(key)
        
        if not (removing and schema_keys):
            return 0
        
        count = 0
        transaction = orb.Transaction()
        transaction.begin()
        for schema, keys in schema_keys.items():
            count += self.removeRecords(schema, keys, options)
        transaction.end()
        
        # update the results
        if count == len(records):
            for record in removing:
                if orb.Table.recordcheck(record):
                    record._removedFromDatabase()
        
        return count
    
    @abstractmethod()
    def removeRecords(self, primaryKeys, options):
        """
        Removes the given records from the inputed schema.  This method is 
        called from the <Connection.remove> method that handles the pre
        processing of grouping records together by schema and only works
        on the primary key.
        
        :param      schema      | <orb.TableSchema>
                    primaryKeys | [<variant> pkey, ..]
                    options     | <orb.DatabaseOptions>
        
        :return     <int> | number of rows removed
        """
        return 0
    
    def restore(self, filename, **options):
        """
        Restores this backend database from the inputed pickle file.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        # save this backup to the database file
        print '0% complete: loading data dump...'
        
        f = open(filename, 'rb')
        data = cPickle.load(f)
        f.close()
        
        items = data.items()
        count = float(len(items))
        db_name = self.database().name()
        i = 0
        
        self.disableInternals()
        options.setdefault('autoCommit', False)
        for schema_name, records in items:
            i += 1
            print '{0:.0%} complete: restoring {1}...'.format(i/count,
                                                              schema_name)
            
            schema = orb.Orb.instance().schema(schema_name,
                                               database=db_name)
            if schema:
                self.setRecords(schema, records, **options)
            else:
                print schema_name, 'not found'
        
        self.enableInternals()
        self.commit()
        
        return True
    
    @abstractmethod()
    def rollback( self ):
        """
        Rollsback the latest code run on the database.
        """
        return False
    
    @abstractmethod()
    def select(self, table_or_join, lookup, options):
        """
        Selects the records from the database for the inputed table or join
        instance based on the given lookup and options.
                    
        :param      table_or_join   | <subclass of orb.Table>
                    lookup          | <orb.LookupOptions>
                    options         | <orb.DatabaseOptions>
        
        :return     [<variant> result, ..]
        """
        return []
    
    def selectFirst(self, table_or_join, lookup, options):
        """
        Returns the first result based on the inputed query options \
        from the database.database.
        
        
        :param      table    | <subclass of Table>
                    lookup   | <orb.LookupOptions>
                    options  | <orb.DatabaseOptions>
        
        :return     <Table> || None
        """
        # limit the lookup information to 1
        lookup.limit = 1
        
        # load the results
        results = self.select( table, query_options, options )
        
        if ( results ):
            return results[0]
        return None
    
    @abstractmethod()
    def setRecords(self, schema, records):
        """
        Restores the data for the inputed schema.
        
        :param      schema  | <orb.TableSchema>
                    records | [<dict> record, ..]
        """
        pass
    
    def setCommitEnabled(self, state):
        """
        Sets whether or not committing changes to the database is currently
        enabled.
        
        :param      state | <bool>
        """
        self._commitEnabled = state
    
    def setColumnEngine(self, columnType, engine):
        """
        Sets the data engine associated with this backend for the given
        column type.
        
        :param      columnType | <orb.ColumnType>
                    engine     | <orb.ColumnEngine>
        """
        self._columnEngines[columnType] = engine
    
    def setEngine(self, engine):
        """
        Returns the table engine associated with this connection backend.
        
        :param     engine | <orb.SchemaEngine>
        """
        self._engine = engine
    
    def setThreadEnabled(self, state):
        """
        Sets whether or not this database backend supports threading.
        
        :param      state | <bool>
        """
        self._threadEnabled = state
    
    def syncRecord(self, record, lookup, options):
        """
        Syncs the record to the current database, checking to \
        see if the record exists, and if so - updates the records \
        field values, otherise, creates the new record.  The possible sync \
        return types are 'created', 'updated', and 'errored'.
        
        :param      record      | <orb.Table>
                    lookup      | <orb.LookupOptions>
                    options     | <orb.DatabaseOptions>
        
        :return     (<str> type, <dict> changeet) || None
        """
        changes = record.changeset()
        if not changes:
            return ('', [])
        
        # create the new record in the database
        if not record.isRecord():
            results = self.insert(record, lookup, options)
            if 'db_error' in results:
                return ('errored', results )
            return ('created', results)
        else:
            results = self.update(record, lookup, options)
            if 'db_error' in results:
                return ('errored', results)
            return ('updated', results)
    
    def syncTable( self, schema, options):
        """
        Syncs the table to the current database, checking to see
        if the table exists, and if so - updates any new columns,
        otherwise, creates the new table.
        
        :param      schema     | <orb.TableSchema>
                    options    | <orb.DatabaseOptions>
        
        :return     ( <str> type, <bool> changed ) || None
        """
        
        if ( self.tableExists(schema, options) ):
            results = self.updateTable(schema, options)
            return ('created', )
        else:
            results = self.createTable(schema, options)
            return ('updated', results)
    
    @abstractmethod()
    def tableExists(self, schema, options):
        """
        Checks to see if the inputed table class exists as a
        database table.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    @abstractmethod()
    def update(self, record, options):
        """
        Updates the database record into the database with the
        given values.
        
        :param      record  | <orb.Table>
                    options | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    @abstractmethod
    def updateTable(self, table, options):
        """
        Determines the difference between the inputed table
        and the table in the database, creating new columns
        for the columns that exist in the table and do not
        exist in the database.
        
        :note       This method will NOT remove any columns, if a column
                    is removed from the table, it will simply no longer 
                    be considered part of the table when working with it.
                    If the column was required by the db, then it will need 
                    to be manually removed by a database manager.  We do not
                    wish to allow removing of columns to be a simple API
                    call that can accidentally be run without someone knowing
                    what they are doing and why.
        
        :param      table    | <orb.TableSchema>
                    options  | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        return False
    
    @staticmethod
    def init():
        """
        Initializes the backend modules for the connection plugin
        system.  Method is called automatically
        """
        if ( Connection.backends ):
            return
        
        plugs = os.environ.get('ORB_BACKEND_PLUGINS')
        if plugs:
            # include any additional backends defined by the environment
            for module in plugs.split(';'):
                if module:
                    try:
                        __import__(module)
                    except ImportError:
                        logger.exception('Could not import backend: %s' % module)
        else:
            # imports the standard plugins
            projex.importmodules(backends)
    
    @staticmethod
    def create( database ):
        """
        Returns a new datbase connection for the inputed database
        from the registered backends and the database type
        
        :return     <Connection> || None
        """
        # initialize the backend plugins
        Connection.init()
        
        # create the backend plugin
        cls = Connection.backends.get(database.databaseType())
        
        if ( not cls ):
            dbtype = database.databaseType()
            err = errors.BackendNotFoundError(dbtype)
            logger.critical(err)
            return None
        
        return cls(database)
    
    @staticmethod
    def register( databaseType, backend ):
        """
        registers the inputed backend class for the given
        database type
                    
        :param      databaseType        <str>
        :param      backend             <subclass of Connection>
        """
        Connection.backends[str(databaseType)] = backend

if os.environ.get('ORB_AUTO_INIT', 'False') == 'True':
    Connection.init()