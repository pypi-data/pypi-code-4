#------------------------------------------------------------------------------#
# Name:        DBMS - DataBases Made Simpler
#
# Purpose:     Small database abstraction library to make it easier to connect
#              and work with a variety of databases in Python. Some adapters
#              already provide much of the functionality provided here, but
#              most do not. DBMS levels the playing field by providing uniform
#              functionality and syntax across all DB API 2 compliant adapters.
#
#              Manages connections, doing automatic imports and providing a
#              uniform connection method to most common databases.
#              Implements DictCursor, NamedTupleCursor and RealDictCursor.
#
# Author:      Scott Bailey, The Evergreen State College, Olympia WA
#
# Created:     05/09/2011
# Licence:     BSD
#------------------------------------------------------------------------------#

__version__ = '1.0.3'
__author__ = 'Scott Bailey <baileys@evergreen.edu>'

import re

from keyword import iskeyword
from helpers import *

try:
    from collections import namedtuple
except ImportError:
    try:
        from collections_backport import namedtuple
    except ImportError:
        print 'for Python < 2.6 download the collections backport'
        print 'http://code.activestate.com/recipes/500261/ or'
        print 'http://gc3pie.googlecode.com/svn-history/r1630/trunk/gc3pie/gc3libs/compat/collections.py'
        raise

#number of queries executed
_nqueries = 0


class DictRow(list):
    """Row object is a memory optimized object that allows access by:
       column name   row['column_name']
       attributes    row.column_name
       column index  row[3]
       slicing       row[1:4]

       DictRow will be dynamically subclassed as dbms.RecordX each
       time a DictCursor is executed.
    """

    __slots__ = ('_columns',)
    # list of column names
    _columns = []

    def __init__(self, *args):
        super(DictRow, self).__init__()
        self[:] = args

    @classmethod
    def setColumns(cls, *args):
        if isinstance(args[0], (list, tuple)):
            cls._columns = args[0]
        else:
            cls._columns = args

    def __getattr__(self, attr):
        if attr in self._columns:
            x = self._columns.index(attr)
            return self[x]

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            item = self._columns.index(item)
        return list.__getitem__(self, item)

    def __setitem__(self, item, val):
        if not isinstance(item, (int, slice)):
            item = self._columns.index(item)
        list.__setitem__(self, item, val)

    def __dir__(self):
        return list(self._columns) + ['copy', 'get', 'items', 'keys', 'values']

    def __str__(self):
        return self.__class__.__name__ + '{' \
            + ', '.join(["'%s': %r" % (k, v) for k, v in self.items()]) + '}'

    def __repr__(self):
        return self.__class__.__name__ + '(' \
            + ', '.join("%r" % v for v in self.values()) + ')'

    def items(self):
        """DictRow.items() -> list of DictRow's (key, value) pairs as 2-tuples"""
        return list(self.iteritems())

    def keys(self):
        """DictRow.keys() -> list of DictRow's keys"""
        return self._columns

    def values(self):
        """DictRow.values() -> list of DictRow's values"""
        return tuple(self[:])

    def has_key(self, key):
        """DictRow.has_key(k) -> True if DictRow has key k, else False"""
        return key in self._columns

    def get(self, key, default=None):
        """DictRow.get(k[,d]) -> DictRow[k] if k in DictRow, else d"""
        try:
            return self[key]
        except ValueError:
            return default

    def iteritems(self):
        """DictRow.iteritems() -> iterator over (key, value) items of DictRow"""
        for i in range(len(self)):
            yield self._columns[i], list.__getitem__(self, i)

    def iterkeys(self):
        """DictRow.iterkeys() -> iterator over keys of DictRow"""
        for key in self._columns:
            yield key

    def itervalues(self):
        """DictRow.itervalues() -> iterator over values of DictRow"""
        return list.__iter__(self)

    def copy(self):
        """DictRow.copy() -> a dict representation of DictRow"""
        return dict(self.iteritems())

#------------------------------------------------------------------------------#
#                       Dictionary Style Cursors
#------------------------------------------------------------------------------#


class Cursor(object):
    """Basic cursor object that returns results as list.
    Designed as the base class for the dictionary type cursors.
    But can also be used like a standard cursor.
    """
    record = None
    columnCase = 'lower'
    debug = False

    def __init__(self, *args, **kwargs):
        self.connection = args[0]

        if 'columnCase' in kwargs:
            self.columnCase = kwargs['columnCase']
            del kwargs['columnCase']
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        try:
            if hasattr(self.connection, '_connection'):
                self._cursor = self.connection._connection.cursor(**kwargs)
            else:
                self._cursor = self.connection.cursor(**kwargs)
        except:
            raise TypeError('First argument must be a database connection object.')

    def __getattr__(self, item):
        return getattr(self._cursor, item)

    def __setattr__(self, key, value):
        if key in ('connection', 'columnCase', 'debug', 'record', '_cursor'):
            self.__dict__[key] = value
        else:
            return setattr(self._cursor, key, value)

    def __dir__(self):
        return dir(self._cursor) + ['columnCase', 'columns', 'connection', 'debug', 'selectinto']

    def __iter__(self):
        if self._isReady():
            return self

    def next(self):
        """Iterate over result set"""
        while True:
            row = self.fetchone()
            if row:
                return row
            else:
                raise StopIteration

    def _rowFactory(self):
        """Initializes the function that will be used to process each record from the result."""
        def row(*args):
            return list(args)
        self.record = row

    def _sanitize(self, colName, idx):
        """Clean up any illegal column names"""
        if colName is None or colName == '':
            # if we didn't get a column name just name it column_X
            return 'column_%d' % (idx + 1)

        # replace any non-word characters with underscore
        colName = re.sub(r'\W+', '_', colName)

        # uppercase if colName is Python keyword
        if iskeyword(colName):
            colName = colName.upper()
        return colName

    def columns(self, case=None):
        """Return list of column names."""
        if self.description:
            if case not in ('upper', 'lower'):
                case = self.columnCase
            if case == 'lower':
                cols = [c[0].lower() for c in self.description]
            elif case == 'upper':
                cols = [c[0].upper() for c in self.description]
            else:
                cols = [c[0] for c in self.description]

            return [self._sanitize(cols[i], i) for i in range(len(cols))]

    def _isReady(self):
        if self._cursor.description is None:
            raise Exception('Query has not been run or did not succeed.')
        if self.record is None:
            self._rowFactory()
        return True

    def debugInfo(self, query, bindvars=()):
        print 'Query:\n%s' % query
        if bindvars:
            print 'Bind vars:\n%s' % bindvars

    def execute(self, query, bindvars=()):
        """Prepare and execute a database operation
        For help on parameters see your connection object's parmHelp()
        """
        global _nqueries
        self.record = None
        _nqueries += 1
        if self.debug:
            self.debugInfo(query, bindvars)
        try:
            ret = self._cursor.execute(query, bindvars)
            if ret is not None and hasattr(ret, 'execute'):
                # interface returns cursor object
                if self._cursor.rowcount > 0:
                    return self._cursor.rowcount
                else:
                    return
            else:
                return ret
        except self.connection.interface.DatabaseError:
            self.debugInfo(query, bindvars)
            raise

    def executemany(self, query, bindvars):
        """Prepare a database operation and execute against all sequences"""
        global _nqueries
        self.record = None
        _nqueries += 1
        if self.debug:
            self.debugInfo(query, bindvars)
        try:
            self._cursor.executemany(query, bindvars)
        except self.connection.interface.DatabaseError:
            self.debugInfo(query, bindvars)
            raise

    def selectinto(self, query, bindvars=()):
        """Run query and return the result. Query must return one and only one row."""
        global _nqueries
        ret = self.execute(query, bindvars)
        _nqueries += 1
        rows = self.fetchmany(2)
        if len(rows) == 0:
            raise self.connection.interface.DatabaseError('No Data Found.')
        elif len(rows) > 1:
            raise self.connection.interface.DatabaseError('selectinto() must return one and only one row.')
        else:
            return rows[0]

    def fetchone(self):
        """Fetch the next row of a query result, returning a single sequence, or None if no more data."""
        if self._isReady():
            row = self._cursor.fetchone()
            if row:
                return self.record(*row)

    def fetchmany(self, size=None):
        """Fetch the next set of rows of a query result, returning a sequence of rows.
        An empty sequence is returned when no more rows are available.

        :param size: The number of rows fetched. If it is not given, the
        cursor's arraysize attribute is used.
        """
        if self._isReady():
            return [self.record(*row) for row in self._cursor.fetchmany(size)]

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning them as a sequence of rows.
        Note the cursor's arraysize attribute can affect the performance of this operation."""
        if self._isReady():
            return [self.record(*row) for row in self._cursor.fetchall()]


class DictCursor(Cursor):
    """Cursor that returns records as DictRow objects. This is the most versatile cursor."""

    def _rowFactory(self):
        # Create a subclass of DictRow to hold returned rows.
        self.record = type('Record%d' % _nqueries,
                        (DictRow,), {'_columns': self.columns()})


class NamedTupleCursor(Cursor):
    """Cursor that returns records as namedtuples."""
    def _rowFactory(self):
        # Create namedtuple type to hold returned rows
        self.record = namedtuple('Record%d' % _nqueries, self.columns())


class RealDictCursor(Cursor):
    """Cursor that returns records as true dicts.

    The memory usage is about 3x that of the other cursor types and they should be
    preferred over the RealDictCursor.
    """

    def _rowFactory(self):
        # create function to map the returned tuple into a dict
        def row(*args):
            return dict(zip(self.columns(), args))
        self.record = row


#------------------------------------------------------------------------------#
#                       Dictionary Style Cursors
#------------------------------------------------------------------------------#


class Connection(object):
    """
    Like a Connection object in the DB API 2.0 specification. But with additional
    helper functions and a reference to the interface and server type.
    """

    def __init__(self, connection, interface):
        self._connection = connection
        self.interface = interface
        # set server type
        if interface.__name__ == 'cx_Oracle':
            self.server = 'oracle'
        elif interface.__name__ in ('psycopg2', 'pgdb'):
            self.server = 'postgres'
        elif interface.__name__ in ('MySQLdb', 'mysql.connector'):
            self.server = 'mysql'
        elif interface.__name__ == 'pymssql':
            self.server = 'mssql'
        elif interface.__name__ == 'sqlite3':
            self.server = 'sqlite'
        elif interface.__name__ == 'pyodbc':
            self.server = 'odbc'
        else:
            self.server = 'unknown'

        # set placeholder
        if self.interface.paramstyle == 'qmark':
            self.placeholder = '?'
        elif self.interface.paramstyle == 'numeric':
            self.placeholder = ':1'
        else:
            self.placeholder = '%s'

    def __getattr__(self, item):
        return getattr(self._connection, item)

    def __setattr__(self, key, value):
        if key in ('_connection', 'interface', 'server', 'placeholder'):
            self.__dict__[key] = value
        else:
            return setattr(self._connection, key, value)

    def __dir__(self):
        return dir(self._connection) + ['interface', 'server',
            'showServerVersion', 'showDatabases', 'showSchemas', 'showTables',
            'showViews', 'showColumns', 'parmHelp', 'placeholder']

    def cursor(self, cursorType=DictCursor):
        """Return new Cursor object.
        If cursorType is not specified, it will return a DictCursor."""
        if cursorType is not None and issubclass(cursorType, Cursor):
            return cursorType(self)
        else:
            return DictCursor(self)

    def parmHelp(self):
        """Print help on this adapter's parameter style."""
        print 'Your adapter\'s parameter style is: %s' % self.interface.paramstyle
        if self.interface.paramstyle == 'qmark':
            print ''''SELECT * FROM people WHERE last_name = ? AND age > ?', ('Smith', 30)'''
        elif self.interface.paramstyle == 'numeric':
            print ''''SELECT * FROM people WHERE last_name = :1 AND age > :2', ('Smith', 30)'''
        elif self.interface.paramstyle == 'named':
            print ''''SELECT * FROM people WHERE last_name = :name AND age > :age', {'name': 'Smith', 'age': 30}'''
        elif self.interface.paramstyle == 'format':
            print ''''SELECT * FROM people WHERE last_name = %s AND age > %s', ('Smith', 30)'''
        elif self.interface.paramstyle == 'pyformat':
            print ''''SELECT * FROM people WHERE last_name = %(name)s AND age > %(age)s', {'name': 'Smith', 'age': 30}'''

    def _execSQL(self, query, bindvars=()):
        """Create a temp cursor, execute query and print the results """
        cur = self.cursor(NamedTupleCursor)
        cur.execute(query, bindvars)
        for row in cur:
            print row

    def showServerVersion(self):
        """Show version of connected server"""
        if self.server == 'oracle':
            sql = 'SELECT * FROM v$version WHERE rownum = 1'
        elif self.server == 'mssql':
            sql = 'SELECT @@version AS "version"'
        else:
            sql = 'SELECT version() AS "version"'
        self._execSQL(sql)

    def showDatabases(self):
        """List all databases/catalogs on this server"""
        if self.server == 'postgres':
            sql = '''SELECT datname AS "database" FROM pg_database WHERE datistemplate=false
                ORDER BY 1'''
        elif self.server == 'oracle':
            print 'Oracle only has one database/instance per server'
            return
        elif self.server == 'mysql':
            sql = '''SELECT ss.schema_name AS "database"
                FROM information_schema.schemata ss
                ORDER BY 1'''
        elif self.server == 'mssql':
            sql = '''SELECT name
                FROM master..sysdatabases
                WHERE sid != 1
                ORDER BY 1'''
        if sql:
            self._execSQL(sql)


    def showSchemas(self):
        """List all schemas on database"""
        if self.server == 'oracle':
            sql = '''SELECT DISTINCT owner AS schema_name FROM dba_objects o
                WHERE o.object_type IN ('TABLE','VIEW') ORDER BY 1'''
        else:
            sql = '''SELECT ss.schema_name
                FROM information_schema.schemata ss
                ORDER BY 1'''
        self._execSQL(sql)


    def showTables(self, schema=None):
        """List all tables, limit to schema if provided"""
        if self.server == 'postgres':
             sql = '''SELECT  table_schema AS schema, table_name
                FROM information_schema.tables t
                WHERE t.table_schema = COALESCE(LOWER(%s), t.table_schema)
                AND t.table_type = 'BASE TABLE'
                ORDER BY 1,2'''
        elif self.server == 'oracle':
            sql = '''SELECT t.owner schema, t.table_name, num_rows
                FROM dba_tables t WHERE t.OWNER = COALESCE(UPPER(:0), t.owner)
                ORDER BY 1,2'''
        elif self.server == 'mysql':
            sql = '''SELECT table_schema AS "schema", table_name, table_rows
                FROM information_schema.TABLES t
                WHERE t.table_schema = COALESCE(LOWER(%s), t.table_schema)
                  AND t.table_type = 'BASE TABLE'
                ORDER BY 1,2''' % self.placeholder
        elif self.server == 'mssql':
            sql = '''SELECT schema_name(t.schema_id) "schema", t.name
                FROM sys.tables t
                WHERE t.schema_id = COALESCE(schema_id(%s), t.schema_id)
                ORDER BY 1, 2''' % self.placeholder
        elif self.server == 'sqlite':
            # sqlite has no schemas and
            sql = '''SELECT name FROM sqlite_master WHERE type = 'table'
                AND ifnull(?, 'grr') IS NOT NULL ORDER BY 1'''

        if sql:
            self._execSQL(sql,(schema,))


    def showViews(self, schema=None):
        """List all views, limit to schema if provided"""
        if self.server == 'oracle':
            sql = '''SELECT owner schema, view_name
                FROM dba_views v
                WHERE v.owner NOT LIKE '%SYS%'
                  AND v.owner = COALESCE(UPPER(:0), v.owner)
                ORDER BY 1,2'''
        elif self.server == 'mssql':
            sql = '''SELECT table_schema AS "schema", table_name  AS "name"
                FROM information_schema.views v
                WHERE v.table_schema = COALESCE(lower(%s), v.table_schema)
                ORDER BY 1,2''' % self.placeholder
        elif self.server == 'sqlite':
            sql = '''SELECT name FROM sqlite_master WHERE type = 'view'
                AND ifnull(?, 'grr') IS NOT NULL ORDER BY 1'''
        else:
            sql = '''SELECT table_schema AS "schema", table_name  AS "name"
                FROM information_schema.views v
                WHERE v.table_schema = COALESCE(lower(%s), v.table_schema)
                ORDER BY 1,2''' % self.placeholder
        self._execSQL(sql, (schema,))

    def showColumns(self, table):
        """List columns from table"""
        sql = 'SELECT * FROM %s WHERE 1=0' % table
        cur = self.cursor()
        cur.execute(sql)
        return cur.columns()