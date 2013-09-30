#!/usr/bin/python

""" 
Defines the main Table class that will be used when developing
database classes.
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

import datetime
import orb

from new import instancemethod

TEMP_REVERSE_LOOKUPS = {}

#------------------------------------------------------------------------------

class gettermethod(object):
    """ Creates a method for tables to use as a field accessor. """
    
    def __init__(self, **kwds):
        """
        Defines the getter method that will be used when accessing
        information about a column on a database record.  This
        class should only be used by the TableBase class when
        generating column methods on a model.
        """
        self.__dict__.update(kwds)
        self.columnName = kwds.get('columnName', '')
        
        self.func_name  = kwds['__name__']
        self.func_args  = '()'
        self.func_doc   = 'Auto-generated Orb getter method for the %s column'
        self.func_doc   %= self.columnName
        
        self.__dict__['__doc__']    = self.func_doc

    def __call__(self, record):
        """
        Calls the getter lookup method for the database record.
        
        :param      record      <Table>
        """
        return record.recordValue(self.columnName, useMethod=False)

#------------------------------------------------------------------------------

class settermethod(object):
    """ Defines a method for setting database fields on a Table instance. """
    
    def __init__( self, **kwds ):
        """
        Defines the setter method that will be used when accessing
        information about a column on a database record.  This
        class should only be used by the TableBase class when
        generating column methods on a model
        """
        self.__dict__.update(kwds)
        self.columnName = kwds.get('columnName', '')
        
        self.func_name  = kwds['__name__']
        self.func_args  = '(value)'
        self.func_doc   = 'Auto-generated Orb setter method for the %s column'
        self.func_doc   %= self.columnName
        
        self.__dict__['__doc__']    = self.func_doc
    
    def __call__( self, record, value ):
        """
        Calls the setter method for the inputed database record.
        
        :param      record      <Table>
                    value       <variant>
        """
        return record.setRecordValue(self.columnName, value, useMethod=False)

#----------------------------------------------------------------------

class reverselookupmethod(object):
    """ Defines a reverse lookup method for lookup up relations. """
    
    def __init__(self, **kwds):
        """
        Defines the getter method that will be used when accessing
        information about a column on a database record.  This
        class should only be used by the TableBase class when
        generating column methods on a model.
        """
        self.__dict__.update(kwds)
        
        self.reference    = kwds.get('reference', '')
        self.referenceDb  = kwds.get('referenceDatabase', None)
        self.columnName   = kwds.get('columnName', '')
        self.unique       = kwds.get('unique', False)
        self.cached       = kwds.get('cached', False)
        self.cacheExpires = kwds.get('cacheExpires', 0)
        self.cache        = {}
        self.cacheStored  = {}
        
        self.func_name  = kwds['__name__']
        self.func_args  = '()'
        self.func_doc   = 'Auto-generated Orb reverse lookup method'
        
        self.__dict__['__doc__']    = self.func_doc
    
    def __call__(self, record, **kwds):
        """
        Calls the getter lookup method for the database record.
        
        :param      record      <Table>
        """
        reload = kwds.pop('reload', False)
        
        # remove any invalid query lookups
        if 'where' in kwds and orb.Query.testNull(kwds['where']):
            kwds.pop('where')
        
        # return from the cache when specified
        cache_key = (id(record), hash(orb.LookupOptions(**kwds)))
        if self.cached:
            results = self.cache.get(cache_key, -1)
            if results != -1:
                if not self.cacheExpires:
                    return results
                    
                stored = self.cacheStored[cache_key]
                seconds = (datetime.datetime.now() - stored).total_seconds()
                
                if seconds < self.cacheExpires and not reload:
                    return results
        
        # lookup the records with a specific model
        table = kwds.pop('model', None)
        if not table:
            table = orb.Orb.instance().model(self.reference,
                                             database=self.referenceDb)
            if not table:
                if self.unique:
                    return None
                return orb.RecordSet()
        
        # make sure this is a valid record
        if not record.isRecord():
            if self.unique:
                return None
            return orb.RecordSet()
        
        if 'where' in kwds:
            where = kwds['where']
            kwds['where'] = (orb.Query(self.columnName) == record) & where
        else:
            kwds['where'] = orb.Query(self.columnName) == record
        
        if not 'order' in kwds and table.schema().defaultOrder():
            kwds['order'] = table.schema().defaultOrder()
        
        # make sure we stay within the same database
        kwds['db'] = record.database()
        
        if self.unique:
            output = table.selectFirst(**kwds)
        else:
            output = table.select(**kwds)
        
        if self.cached and \
           (output is not None or self.cacheExpires):
            self.cache[cache_key] = output
            self.cacheStored[cache_key] = datetime.datetime.now()
        return output

#------------------------------------------------------------------------------

class TableBase(type):
    """ 
    Defines the table Meta class that will be used to dynamically generate
    Table class types.
    """
    def __new__( mcs, name, bases, attrs ):
        """
        Manages the creation of database model classes, reading
        through the creation attributes and generating table
        schemas based on the inputed information.  This class
        never needs to be expressly defined, as any class that
        inherits from the Table class will be passed through this
        as a constructor.
        
        :param      mcs         <TableBase>
        :param      name        <str>
        :param      bases       <tuple> (<object> base,)
        :param      attrs       <dict> properties
        
        :return     <type>
        """
        # ignore initial class
        db_ignore = attrs.pop('__db_ignore__', False)
        if db_ignore:
            return super(TableBase, mcs).__new__(mcs, name, bases, attrs)
        
        # collect database and schema information
        db_data     = {}
        db_data['__db_name__']      = name
        db_data['__db_columns__']   = []
        db_data['__db_indexes__']   = []
        db_data['__db_pipes__']     = []
        db_data['__db_schema__']    = None
        
        for key, value in attrs.items():
            if key.startswith('__db_'):
                db_data[key] = attrs.pop(key)
                keys_found = True
        
        # make sure we have are creating a new database table class
        parents = [base for base in bases if isinstance(base, TableBase)]
        
        # set the database name for this table
        if parents:
            db_data.setdefault('__db__', parents[0].__db__)
        else:
            db_data.setdefault('__db__', '')
        
        # merge inherited information
        for parent in parents:
            for key, value in parent.__dict__.items():
                # skip non-db values
                if not key.startswith('__db_'):
                    continue
                
                db_data.setdefault(key, value)
            
        # determine if this is a definition, or a specific schema
        new_class   = super(TableBase, mcs).__new__(mcs, name, bases, attrs)
        schema      = db_data.get('__db_schema__')
        
        if schema:
            new_columns = db_data.get('__db_columns__', [])
            cur_columns = schema.columns(recurse=False, includeProxies=False)
            columns     = cur_columns + new_columns
            indexes     = schema.indexes() + db_data.get('__db_indexes__', [])
            pipes       = schema.pipes() + db_data.get('__db_pipes__', [])
            tableName   = schema.tableName()
            
            schemaName  = schema.name()
            schema.setColumns(columns)
            schema.setIndexes(indexes)
            schema.setPipes(pipes)
            
        else:
            dbname       = db_data.get('__db__',            '')
            abstract     = db_data.get('__db_abstract__',   False)
            columns      = db_data.get('__db_columns__',    [])
            indexes      = db_data.get('__db_indexes__',    [])
            pipes        = db_data.get('__db_pipes__',      [])
            schemaName   = db_data.get('__db_name__',       name)
            schemaGroup  = db_data.get('__db_group__',      'Default')
            tableName    = db_data.get('__db_tablename__',  '')
            inherits     = db_data.get('__db_inherits__',   '')
            autoPrimary  = db_data.get('__db_autoprimary__', True)
            
            if not '__db_inherits__' in db_data:
                if parents and parents[0].schema():
                    inherits = parents[0].schema().name()
            
            # create the table schema
            schema  = orb.TableSchema()
            schema.setDatabaseName( dbname )
            schema.setAutoPrimary( autoPrimary )
            schema.setName( schemaName )
            schema.setGroupName( schemaGroup )
            schema.setTableName( tableName )
            schema.setAbstract( abstract )
            schema.setColumns( columns )
            schema.setIndexes( indexes )
            schema.setPipes( pipes )
            schema.setInherits( inherits )
            schema.setModel(new_class)
            
            orb.Orb.instance().registerSchema(schema)
        
        db_data['__db_schema__'] = schema
        
        # add the db values to the class
        for key, value in db_data.items():
            setattr(new_class, key, value)
        
        # create class methods for the index instances
        for index in indexes:
            iname = index.name()
            if not hasattr(new_class, iname):
                setattr(new_class, index.name(), classmethod(index))
        
        # create instance methods for the pipe instances
        for pipe in pipes:
            pname = pipe.name()
            if not hasattr(new_class, pname):
                pipemethod = instancemethod(pipe, None, new_class)
                setattr(new_class, pname, pipemethod)
        
        # pylint: disable-msg=W0212
        for column in columns:
            colname = column.name()
            
            # create getter method
            gname = column.getterName()
            if gname and not hasattr(new_class, gname):
                gmethod = gettermethod( columnName=colname,
                                        __name__ = gname )
                                        
                getter  = instancemethod(gmethod, None, new_class)
                setattr(new_class, gname, getter)
            
            # create setter method
            sname = column.setterName()
            if sname and not (column.isReadOnly() or hasattr(new_class, sname)):
                smethod = settermethod(columnName = colname, __name__ = sname)
                setter  = instancemethod(smethod, None, new_class)
                setattr(new_class, sname, setter)
            
            # create an index if necessary
            iname = column.indexName()
            if column.indexed() and iname and not hasattr(new_class, iname):
                index = orb.Index(iname,
                                  [column.name()],
                                  unique=column.unique())
                index.setCached(column.indexCached())
                index.setCachedExpires(column.indexCachedExpires())
                index.__name__ = iname
                imethod = classmethod(index)
                setattr(new_class, iname, imethod)
            
            # create a reverse lookup
            if column.isReversed() and column.schema().name() == schemaName:
                rev_name   = column.reversedName()
                rev_cached = column.reversedCached()
                ref_name   = column.reference()
                ref_model  = column.referenceModel()
                rev_cacheExpires = column.reversedCacheExpires()
                
                # create the lookup method
                lookup = reverselookupmethod(columnName   = column.name(),
                                             reference    = schemaName,
                                             unique       = column.unique(),
                                             cached       = rev_cached,
                                             cacheExpires = rev_cacheExpires,
                                             __name__     = rev_name)
                
                # ensure we're assigning it to the proper base module
                while ref_model and \
                      ref_model.__module__ != 'orb.tablebase' and \
                      ref_model.__bases__:
                    ref_model = ref_model.__bases__[0]
                
                # assign to an existing model
                if ref_model:
                    ilookup = instancemethod(lookup, None, ref_model)
                    setattr(ref_model, rev_name, ilookup)
                else:
                    TEMP_REVERSE_LOOKUPS.setdefault(ref_name, [])
                    TEMP_REVERSE_LOOKUPS[ref_name].append((rev_name, lookup))
        
        # assign any cached reverse lookups to this model
        if schemaName in TEMP_REVERSE_LOOKUPS:
            lookups = TEMP_REVERSE_LOOKUPS.pop(schemaName)
            for rev_name, lookup in lookups:
                ilookup = instancemethod(lookup, None, new_class)
                setattr(new_class, rev_name, ilookup)
                
        return new_class