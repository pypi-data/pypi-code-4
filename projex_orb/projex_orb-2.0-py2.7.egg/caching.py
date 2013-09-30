#!/usr/bin/python

""" 
Defines caching methods to use when working with tables.
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

import datetime
import logging
import orb

from orb import errors, settings

import projex.text
from projex.decorators import wraps

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class OrderCompare(object):
    def __init__( self, order ):
        self._order = order
    
    def __call__( self, a, b ):
        for col, direction in self._order:
            a_val = a.get(col)
            b_val = b.get(col)
            
            # ignore same results
            result = cmp(a_val, b_val)
            if ( result == 0 ):
                continue
            
            if ( direction == 'desc' ):
                return -result
            return result
        return 0

#-------------------------------------------------------------------------------

class DataCache(object):
    """
    This class is used to store custom properties on individual records via
    the <orb.Table.dataCache> method.
    """
    def __init__( self ):
        self._cache = {}
    
    def clear( self ):
        """
        Clears all the cache data from this record.
        """
        self._cache.clear()
    
    def isCached( self, key ):
        """
        Returns whether or not this cache instance has the given key cached.
        
        :param      key | <str>
        
        :return     <bool>
        """
        return str(key) in self._cache
    
    def setValue( self, key, value ):
        """
        Sets the value for the key in the cache to the given value.
        
        :param      key   | <str>
                    value | <variant>
        """
        self._cache[str(key)] = value
    
    def value( self, key, default = None ):
        """
        Returns the value from the inputed cache key.  If no value is found,
        the default value is returned.
        
        :param      key     | <str>
                    default | <variant>
        """
        return self._cache.get(str(key), default)

#------------------------------------------------------------------------------

class RecordCache(object):
    """
    Defines a key cache class for the table to use when caching records from the
    system.  Caching is defined on the TableSchema class, see 
    TableSchema.setCachingEnabled for more info.
    
    :usage      |from orb import RecordCache
                |
                |with RecordCache(User, AccountType):
                |   for transaction in Transactions.select():
                |       print transaction.transferredBy()  # lookups up from
                |                                          # the user cache
                
                |from orb import Table
                |
                |class User(Table):
                |   __db_cached__ = True
                |
                |User.select() # looks up from the RecordCache for the table
    """
    def __init__(self, *tables):
        self._tables  = list(tables) # [<orb.Table>, ..]
        self._cache   = {} # {<str> table_name: {<variant> pkey: <variant> val}}
        self._updated = {} # {<str> table_name: <datetime>}
        self._expires = {} # {<str> table_name: <int> minutes}
        self._select  = {} # {(<str> table_name, <str> lookup, <str> options): [<dict> record, ..], ..}
        self._preloaded = {}
        
        # cache all tables
        if not tables:
            tables = orb.Orb.instance().models()
        
        # set the default caching value to 5 minutes
        for table in tables:
            self._expires[table] = 5
    
    def __enter__(self):
        self.begin()
    
    def __exit__(self):
        self.end()
    
    def begin(self):
        """
        Begins the caching process for this instance.
        """
        for table in self._tables:
            table.pushRecordCache(self)
    
    def clear(self, table=None):
        """
        Clears the current cache information.
        """
        if table:
            for d in (self._cache, self._updated, self._expires):
                try:
                    d.pop(table.__name__)
                except IndexError:
                    pass
            
            for key in self._select.keys():
                if key[0] == table.__name__:
                    self._select.pop(key)
        else:
            self._cache.clear()
            self._updated.clear()
            self._expires.clear()
            self._select.clear()
    
    def count(self, backend, table, lookup, options):
        """
        Returns the number of entries based on the given options.
        
        :param      backend | <orb.Connection>
                    table   | <subclass of orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     <int>
        """
        options.inflateRecords = False
        return len(self.select(backend, table, lookup, options))
    
    def distinct(self, backend, table, lookup, options):
        """
        Returns a distinct set o fentries based on the given lookup options.
        
        :param      table   | <subclass of orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        output = dict([(column, set()) for column in lookup.columns])
        for record in self.select(backend, table, lookup, options):
            for column in lookup.columns:
                output[column].add(record.get(column))
        
        for key, value in output.items():
            output[key] = list(value)
        
        return output
    
    def end(self):
        """
        Ends the caching process for this instance.
        """
        for table in self._tables:
            table.popRecordCache()
    
    def isValid(self, table, query=None):
        """
        Returns whether or not this cache is currently valid.
        
        :return     <bool>
        """
        # check to see if we have looked up results for this query
        query_key   = query.toXmlString()
        last_update = self._updated.get(table.__name__, {}).get(query_key)
        
        if last_update is None:
            return False
        
        # if the values never expire, then one of our options succeeded
        expires = self._expires.get(table.__name__, 0)
        if not expires:
            return True
        
        # determine if the cache is out of date by comparing the current
        # time against the last updated time
        time_delta = datetime.datetime.now() - last_update
        if (time_delta.seconds / 60) > expires:
            self._cache[table.__name__].pop(query_key)
            return False
        
        return True
    
    def preload(self, table):
        """
        Preloads the records for the given table.
        
        :param      table | <orb.Table>
        """
        self._preloaded[table] = self.records(table)
    
    def preloadedRecords(self, table, lookup):
        """
        Looking up pre-loaded record information.
        
        :param      table  | <orb.Table>
                    lookup | <orb.LookupOptions>
        
        :return     [<dict> data, ..]
        """
        records = self._preloaded.get(table, [])
        if lookup.order:
            records = sorted(records, OrderCompare(lookup.order))
        
        if lookup.start:
            start = lookup.start
        else:
            start = 0
        
        if lookup.distinct:
            output = set()
        else:
            output = []
        
        for r in range(start, len(records)):
            record = records[r]
            
            # ensure we're looking up a valid record
            if lookup.where and not lookup.where.validate(record):
                continue
            
            if lookup.columns:
                record = [(key,val) for key, val in record.items() \
                          if key in lookup.columns]
            else:
                record = record.items()
            
            # ensure we have unique ordering for distinct
            record.sort()
            if lookup.distinct and record in output:
                continue
            
            output.append(record)
            if lookup.limit and len(output) == record:
                break
        
        return map(dict, output)
    
    def record(self, table, primaryKey):
        """
        Returns a record for the given primary key.
        
        :return     {<str> columnName: <variant> value, ..} record
        """
        lookup = orb.LookupOptions()
        lookup.where = Q(table) == primaryKey
        options = orb.DatabaseOptions()
        return self.selectFirst(table.getDatabase().backend(),
                                table,
                                lookup,
                                options)
    
    def records(self, table, query=None):
        """
        Returns a list of records that are cached.
        
        :param      table | <orb.Table>
                    query | <orb.Query> || None
        
        :return     [<Table>, ..]
        """
        lookup = orb.LookupOptions()
        lookup.where = query
        options = orb.DatabaseOptions()
        return self.select(table.getDatabase().backend(),
                           table,
                           lookup,
                           options)
        
    def setExpires(self, table, minutes):
        """
        Sets the length of time in minutes to hold onto this cache before 
        re-querying the database.
        
        :param      minutes | <int> || <float>
        """
        self._expires[table.__name__] = minutes
    
    def selectFirst(self, backend, table, lookup, options):
        """
        Returns a list of records from the cache that matches the inputed
        parameters.
        
        :param      table   | <orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     <dict> record || None
        """
        lookup.limit = 1
        results = self.select(backend, table, lookup, options)
        if results:
            return results[0]
        return None
    
    def select(self, backend, table, lookup, options):
        """
        Returns a list of records from the cache that matches the inputed
        parameters.
        
        :param      backend | <orb.Connection>
                    table   | <orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     [<dict> record, ..]
        """
        key = (table.__name__,
               backend.database().name(),
               hash(lookup),
               hash(options))
        
        # check to see if the exact query has already been performed
        if key in self._select:
            return self._select[key]
        
        # use simple query options for non-joined queries
        elif self._preloaded.get(table) and \
             (lookup.where is None or lookup.where.tables() in ([table], [])):
            output = self.preloadedRecords(table, lookup)
            self._select[key] = output
            return output
        
        # otherwise lookup and cache data
        if lookup.where is not None:
            query_key = lookup.where.toXmlString()
        else:
            query_key = None
        
        try:
            records = backend.select(table, lookup, options)
        except errors.OrbError, err:
            if options.throwErrors:
                raise
            else:
                logger.debug('Backend error occurred.\n%s', str(err))
                records = []
            
        self._select[key] = records
        self._updated.setdefault(table.__name__, {})
        self._updated[table.__name__][query_key] = datetime.datetime.now()
        return records
        
    def tables(self):
        """
        Returns the tables linked with this cache set.
        
        :return     [<orb.Table>, ..]
        """
        return self._tables