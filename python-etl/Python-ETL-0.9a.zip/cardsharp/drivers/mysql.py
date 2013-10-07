# Copyright (c) 2010 NORC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Softwa
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWA

from __future__ import division, unicode_literals, absolute_import

from . import Loader, Saver, register, SrcLoader, SrcSaver
from .options import option, after, loads, saves
from ..errors import *
from ..variables import Variable, VariableSpec
from ..util import memoize
from contextlib import closing
from threading import Lock
from itertools import izip_longest
from _mysql_exceptions import IntegrityError, OperationalError
from re import sub, search
import _mysql
from MySQLdb import connect
#from memcache import Client

#TODO: create namespace for each driver and then have options file in that namespace to store all the option methods
'''Name of host to connect to. Default: use the localhost'''
@option(default = 'localhost')
def host(options):
    pass

'''The user name used to connect to MySQL.'''
@option(required = True)
def user(options):
    pass

'''The password for the user account on server.'''
@option(default = None)
def pwd(options):    
    pass

'''The database to use.'''
@option(required = True)
def source(options):
    pass

"""TCP port of MySQL server. Default: standard port (3306)."""
@option(default = 3306, convert = int)
def port(options):
    pass

"""Dataset is equivalant to a MySQL table."""
@option(required = True)
def dataset(options):
    pass

"""Set overwrite to True to drop and create new table if the table currently exists."""
@option(default = False)
def overwrite(options):
    pass

"""Set **update** to True to change existing values in a table. Must also specify **where** option."""
@option(default = False)
def update(options):
    if options.get('overwrite') and options.get('update'):
        raise OptionError("Overwrite and update options can not both be set to True")

"""Set **update** to True to change existing values in a table. Must also specify **where** option."""
@saves
@option(default = False)
def replace(options):
    if options.get('overwrite') and options.get('update'):
        raise OptionError("Overwrite and replace options can not both be set to True")
    
@loads
@option(default = None)
def select(options):
    """A list of variable names to select from the dataset."""
    pass

"""When **update** is set to True specify a column in where option. This column must be the primary_id 
of the table."""
@saves
@option(default = None)
def where(options):
    #TODO modify to all list of variable names and condition
    #takes one varname and matches row value to it
    if options.get('where') and not options.get('update'):
        raise OptionError("""Set update to True for where clause to take effect when saving.""")

@loads
@option(default = None)
def where(options):
    pass

@loads
@option(default = None)
def sql_limit(options):
    """Option to specify limit string for load query"""
    pass

"""Set **append** to True to add values to existing table."""
@option(default = False)
def append(options):
    if options.get('overwrite') and options.get('append'):
        raise OptionError("Overwrite and append options can not both be set to True.")
    elif options.get('append') and options.get('update'):
        raise OptionError("Append and update options can not both be set to True.")

"""Specify encoding to set the character set on the database"""
@option(default = 'utf8')
def encoding(options):
    pass

'''Specify collate to set the collation on the character set on the database'''
@saves
@option(default = 'utf8_unicode_ci')
def collate(options):
    pass

'''Decimal precision = M in DECIMAL(M, D) where M is the Maximum number of digits (1 to 65)'''
@option(default = 28)
def precision(options, convert = int):
    try:        
        d_p = options['precision']
        
        assert(d_p > 0 and d_p < 66) 
    except:
        raise OptionError('Invalid decimal precision must be an int and greater than 0 and less than 66')
    

'''Decimal scale = D in DECIMAL(M, D) where D is the number of digits to the right of the decimal'''
@option(default = 12)
def scale(options , convert = int):
    try: 
        assert (options['scale'] >= 0) 
    except:
        raise OptionError('Invalid decimal precision must be an int and greater than 0')

'''constraints for the dataset to be added to the MySQL table via CREATE TABLE'''
@saves
@option(default = None)
def constraints(options):
    pass

@option(default = 255, convert = int)
def max_string_width(options):
    if options['max_string_width'] < 1:
        raise OptionError('max_string_width must be greater than 0.')

@option(default = None)
def cache_key(options):
    pass

@option(default = {})
def cache_type(options):
    pass

@option(default = False)
def as_cache(options):
    pass

#TODO figure out how to add None to list when not 
#specified instead of raising error
@loads
@option(default = [None])
def load_as_null(options):
    '''List of values that should be loaded as a null value'''
    pass
    
@saves
@option(default = [None])
def save_as_null(options):
    '''List of values that should be saved as a null value.'''
    if None not in options['save_as_null']:
        raise OptionError('Must include None in save_as_null list')

#@option(default = ['127.0.0.1:11211', 0])
#def memcache(options):
#    pass

def _conv_var(var, value, opt):
    if value in opt['save_as_null']:
        return str('null')
    
    key = var.format.key
    
    def _check_date(val):
        min_year = 1000 
        
        if val.year < min_year:
            raise SaveError('%i is an invalid datetime: year less than %i' % (val.year, min_year))
        
        return val
    
    if key == 'string':
        #TODO - allow full unicode range
        s_o = var.flags.string_width_override if var.flags.string_width_override else False
        length = var.rules.length or opt['max_string_width']
        
        if len(value) > length:
            raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (var.name, len(value), length))
        #print '"' + str(value.replace('"', '\\"')) + '"'
        return ''.join(['"', _mysql.escape_string(value), '"'])

    elif key == 'decimal':
        return str(value)
    
    elif key in ['datetime', 'date']:
        _check_date(value)
        return str(value)
    
    elif key == 'time':
        return str(value)
    
    elif key == 'boolean':
        return '1' if value == True else '0'
    
    #default     
    return str(value)

def _conv_var_load(var, value, **kw):
    if var.format.key == 'string':
        if value in kw.get('load_as_null'):
            return None
        
    elif var.format.key == 'boolean':
        return True if value == 1 else False
        
    return value

#TODO import conv=conversion instead of creating our own conversion functions 
_connection_lock = Lock()
def _get_cnxn(opt):
    with _connection_lock:
        return connect(host = opt['host'], user = opt['user'], passwd = opt['pwd'], charset = opt['encoding'],
                       db = opt['source'], port = opt['port'] ,use_unicode=True)

def _get_var_type(var, opt):
    key = var.format.key
    n_n = 'NOT NULL' if (var.rules.not_null or var.flags.not_null) else ''
    a_i = ''
    if var.flags.auto_inc:
        if key != 'integer':
            raise SaveError("Auto_increment can only be set on format of integer not %s" % var.format)
        a_i = 'AUTO_INCREMENT'
            
    s_o = var.flags.string_width_override if var.flags.string_width_override else False 
    
    if key == 'string':
        length = var.rules.length or opt['max_string_width']
        
        #TODO: add test for below SaveError
        if length > opt['max_string_width'] and not s_o:                                
            raise SaveError(''.join(['Cannot create variable (%s) with a length of %s (maximum width %s). ',
                                    'To create enable string_width_override rule.']) % (var.name, length, opt['max_string_width'])) 
        elif length <= 21843:
            #use national varchar for unicode encoding 
            char_type = 'nvarchar' if opt['encoding'] != 'latin1' else 'varchar'
            return '%s(%s) %s' % (char_type, length, n_n)
            
        else:
            if opt['encoding'] == 'latin1':
                return 'longtext' % n_n
            else:
                raise SaveError('Cannot save variable %s with length %s to non latin1-encoding' % (var.name, length, opt['max_string_width']))
    
    elif key == 'integer':
        #TODO if length rule present use length to determin datatype (tinyint vs smallint, vs mediumint, etc
        return 'int %s %s' % (n_n, a_i)
    
    elif key in ('float', 'double', 'date', 'time', 'datetime', 'boolean'):
        if key in ('float', 'double') and (var.rules.precision or var.rules.scale):
            percision = var.rules.precision or opt['precision']
            scale = var.rules.scale if var.rules.scale is not None else opt['scale']
            return 'decimal(%s, %s) %s' % (percision, scale, n_n)
        else:
            return '%s %s' % (key, n_n)    
    
    elif key == 'decimal':
        percision = var.rules.precision or opt['precision']
        scale = var.rules.scale if var.rules.scale is not None else opt['scale']
        return 'decimal(%s, %s) %s' % (percision, scale, n_n)   
    
#    elif key == 'binary':
#        length = var.rules.length or opt['max_string_width']
#        #TODO add tests
#        if length > opt['max_string_width'] and not var.flags.string_width_override:                                
#            raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (var.name, length, string_width))
#        elif length > 21843: 
#            raise SaveError('Cannot save variable (%s) with a length of %s (maximum width 21843)' % (var.name, length))
#        else:
#            return 'varbinary(%s) %s' % (length, n_n)
         
    raise SaveError('Cannot save datatype %s to MySQL' % key)

def _check_constraint(var, opt):
    key = var.format.key
    if key == 'string':
        length = var.rules.length or opt['max_string_width']
        if length > 255:
            raise SaveError("""String variable: %s can not have primary key set as constraint 
                                when max_string_width not set or is greater than 255""" % var.name)
def _get_key_constraints(var, opt, var_text):
    c_text = ''
    pk = var.flags.primary_key
    fk = var.flags.foreign_key
    u = var.flags.unique
    if pk:
        _check_constraint(var, opt)
        pk_name = search('%s(?= PRIMARY KEY)' % pk, var_text)
        pk_orig = search('(?<=PRIMARY KEY \().*(?=\))', var_text)
        if not pk_name and pk_orig:
            raise SaveError('PRIMARY KEY on multiple variables with non-matching PRIMARY KEY identifier. %s != %s')
        elif pk_name:
            var_text = sub('(?<=PRIMARY KEY \().*(?=\))', '%s, %s' %(pk_orig.group(), var.name), var_text)
        else:
            var_text = '%s, CONSTRAINT %s PRIMARY KEY (%s)' % (var_text, pk, var.name)
            
    if fk:
        _check_constraint(var, opt)
        fk_name = search('%s(?= FOREIGN KEY)' % fk[0], var_text)
        fk_orig = search('(?<=FOREIGN KEY \().*(?=\) )', var_text)
        if fk_name:
            var_text = sub('(?<=CONSTRAINT %s FOREIGN KEY \().*(?=\) )' % fk[0], 
                              '%s, %s' %(fk_orig.group(), var.name), var_text)
        else:
            var_text = '%s, CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s' % (var_text, fk[0], var.name, fk[1])
    
    if u:
        _check_constraint(var, opt)
        u_name = search('%s(?= UNIQUE)' % u, var_text)
        u_orig = search('(?<=UNIQUE \().*(?=\) )', var_text)
        if u_name:
            var_text = sub('(?<=CONSTRAINT %s UNIQUE \().*(?=\) )' % u, 
                              '%s, %s' %(u_orig.group(), var.name), var_text)
        else:
            var_text = '%s, CONSTRAINT %s UNIQUE (%s)' % (var_text, u, var.name)
            
    return var_text

class MySQLOdbcHandler(SrcLoader, SrcSaver):
    id = 'cardsharp.drivers.mysql'
    formats = ('mysql', )
    
    def list_datasets(self, options):
        with closing(_get_cnxn(options)) as cnxn:
            with closing(cnxn.cursor()) as cursor:
                cursor.execute('show tables')
                return [table[0] for table in cursor.fetchall()]
    
    def drop(self, options):
        with closing(_get_cnxn(options)) as cnxn:
            with closing(cnxn.cursor()) as cursor:                
                try:
                    cursor.execute('DROP TABLE %s' % options['dataset'])
                
                except IntegrityError as IntErr:
                    raise SaveError("Unable to drop dataset %s. IntegrityError #%r, %s" % (
                                        options['dataset'], IntErr.args[0],IntErr.args[1]))
        
                except OperationalError as OptErr:
                    raise SaveError("Unable to drop dataset %s. OperationalError #%r, %s"  % (
                                    options['dataset'], OptErr.args[0], OptErr.args[1]))
                
    def get_dataset_info(self, options):
        with closing(_get_cnxn(options)) as cnxn:
            col_names = 'and (%s)' % ' or '.join(['column_name = "%s"' % c_n for c_n in options['select']]) if options.get('select') else ''
            with closing(cnxn.cursor()) as c:
                c.execute("""SELECT VERSION()""")
                version = c.fetchone()[0].split('.')
                
                col_info  = [3, 14, 6, 16, 10, 11] if int(version[1]) < 6 else [3, 15, 6, 17, 10, 12]
                c.execute("""SELECT * FROM information_schema.columns 
                             WHERE table_name = '%s' 
                               and table_schema = '%s' 
                               %s""" %( options['dataset'], options['source'], col_names))
                vars = []
                
                for var_desc in c.fetchall():
                    #get name, type, not null, primary_key, auto increment, 
                    #precision and scale information
                    name, type, null, a_i, p, s  = (var_desc[x] for x in col_info)
                    
                    kw = {}
                    kw[str('not_null')] = True if null == 'NO' else False
                    '''Auto_inc will not be set if variable also has UNIQUE constraint due to limitation of
                    MySQL information schema tables. Extra information column only contains one value, not list
                    of values, and unique has higher priority.'''
                    
                    if a_i == 'auto_increment':
                        kw[str('auto_inc')] = True
                    
                    elif a_i == 'UNI':
                        kw[str('unique')] = True
                        
                    if p:
                        kw[str('precision')] = int(p)
                    if s: 
                        kw[str('scale')] = int(s)
                    
                    #handle string types
                    #Data types currently not supported: BIT,text...[binary], ENUM, SET, year
                    if search('char', type):    
                        kw[str('length')] = int(search('(?<=\()\d*(?=\))', type).group())
                        v = Variable(name, 'string', **kw)
                    
                    elif search('binary', type):
                        kw[str('length')] = int(search('(?<=\().*(?=\))', type).group())
                        v = Variable(name, 'binary', **kw)
                    
                    elif search('text|blob', type):
                        v = Variable(name, 'string', **kw)
                    
                    #handle numeric types
                    elif search('int', type):
                        if type == 'tinyint(1)':
                            kw[str('precision')] = None
                            v = Variable(name, 'boolean', **kw)
                        else:
                            kw[str('length')] = int(search('(?<=\().*(?=\))', type).group())
                            v = Variable(name, 'integer', **kw)
                    
                    elif search('bool', type):
                        v = Variable(name, 'boolean', **kw)
                    
                    elif search('float|double|real', type):
                        v = Variable(name, 'float', **kw)
                    
                    elif search('decimal|numeric', type):
                        v = Variable(name, 'decimal', **kw)
                    
                    #handle date and time types
                    elif type == 'date':
                        v = Variable(name, 'date', **kw)
                    
                    elif type == 'datetime':
                        v = Variable(name, 'datetime', **kw)
                    
                    #mysqldb returns time as timedelta
                    elif type == 'time':
                        v = Variable(name, 'timedelta', **kw)
                    
                    elif type == 'timestamp':
                        v = Variable(name, 'datetime', **kw)
                    
                    else:
                        raise LoaderError('Datatype not supported: %r' % type_code)
                    
                    c.execute("""SELECT * 
                                 FROM information_schema.key_column_usage 
                                 WHERE table_name = '%s' 
                                   and column_name = '%s'"""  % (options['dataset'], name))
                    
                    keys = c.fetchall()
                    
                    for key in keys:
                        #key[2] = constraint_name
                        #key[6] = column_name
                        #key[10] = references table name
                        #key[11] = referenced_column_name
                        if key[2] == 'PRIMARY': 
                            v.flags.primary_key = key[6] 
                        if key[10]: 
                            v.flags.foreign_key = (key[2], '%s(%s)' % (key[10], key[11])) 
                
                    vars.append(v)
                    
                c.execute('SELECT COUNT(*) FROM %s' % options['dataset'])
                
                options['_cases'] = int(c.fetchone()[0])
                options['_variables'] = VariableSpec(vars)
                options['format'] = 'mysql'

    def can_load(self, options):
        if options.get('format').lower() == 'mysql':
            return 5000

        return 0
   
    class loader(Loader):
        def rows(self):
        #TODO: Add ability to load into a dataset that already contains data, 
        #if can add validation on columns
            opt = self.options
            where = ''.join(['WHERE ', opt['where']]) if opt['where'] else ''
            limit = ''.join(['LIMIT ', opt['sql_limit']]) if opt['sql_limit'] else ''
            #TODO add keep and drop for load in select statement
            with closing(_get_cnxn(opt)) as cnxn:
                with closing(cnxn.cursor()) as cursor:
                    cols = ','.join([v.name for v in opt['_variables']])
                    cursor.execute('SELECT %s FROM %s %s %s' % (cols, opt['dataset'], where, limit))
                    
                    for row in opt['_filter'].filter(cursor.fetchall()):
                        yield (_conv_var_load(var, value, **opt) for var, value in opt['_variables'].pair_filter(row))
                        
    def can_save(self, options):
        if options.get('format') == 'mysql':
            return 5000

        return 0
    
    class saver(Saver):
        def rows(self):
            opt = self.options
          
            def _get_where(): 
                where = ''.join([opt['where'], '=', _conv_var(opt['_variables'][opt['where']], row[opt['where']], opt)]) 
                return where
            
            with closing(_get_cnxn(opt)) as cnxn:
                with closing(cnxn.cursor()) as c:    
                    #add variables with constraints for table creation if needed
                    var_text = ', '.join('%s %s' % 
                        (v.name, _get_var_type(v, opt)) for v in opt['_variables'].filter())
                    
                    #add primary and foreign key constraints defined on variable as constraint rule
                    for v in opt['_variables'].filter():
                        var_text =  _get_key_constraints(v, opt, var_text)
                    
                    #add constraint string
                    if opt['constraints']:
                        var_text = '%s, %s' % (var_text, opt['constraints'])
                    
                    #get tables currently in database
                    c.execute('SHOW TABLES FROM %s' % opt['source'])
                    tbl_names = [table[0] for table in c.fetchall()]
                    table_columns = ''
                    
                    #if dataset name already in database as table check to see 
                    #if columns match variables
                    if opt['dataset'].lower() in tbl_names:
                        c.execute('SHOW COLUMNS FROM %s' % opt['dataset'])
                        
                        table_columns = [col[0] for col in c.fetchall()]
                        
                        col_match = True
                        col_count = 0
                        
                        for var1, var2 in izip_longest(table_columns, opt['_variables']):
                            if 'drop' in opt and var1 in opt['drop']:
                                col_match = False  
                            else: 
                                col_match = True
                                
                            col_count += 1
                            
                            if var1 != var2.name.lower():
                                col_match = False
                                break
                    
                    
                    #TODO fix this and test it
                    if 'keep' in opt:
                        num_vars = len(opt['_variables']) - len(opt['keep']) 
#                    elif 'drop' in opt:
#                        num_vars = col_count
                    else: 
                        num_vars = len(opt['_variables'])
                    
                    if opt['dataset'].lower() not in tbl_names:
                        print "CREATE TABLE %s (%s) CHARACTER SET %s COLLATE %s" % (opt['dataset'], var_text, opt['encoding'], opt['collate'])
                        c.execute("CREATE TABLE %s (%s) CHARACTER SET %s COLLATE %s" % 
                                    (opt['dataset'], var_text, opt['encoding'], opt['collate']))
                        
                        cnxn.commit()
                        
                    elif opt['overwrite'] == True:
                            try:
                                c.execute("DROP TABLE %s" % opt['dataset'])
                                c.execute("CREATE TABLE %s (%s) CHARACTER SET %s COLLATE %s" % (
                                             opt['dataset'], var_text, opt['encoding'], opt['collate']))
                                cnxn.commit()
                                
                            except IntegrityError as IntErr:
                                raise SaveError("Unable to overwrite table %s. #%r, %s" %(opt['dataset'], IntErr.args[0], IntErr.args[1]))
                    
                    elif opt['append'] == False and opt['update'] == False and opt['replace'] == False:
                        raise SaveError("Table %s already exists and overwrite, append, replace, or update not set." % opt['dataset'])
                    
#                    elif col_match == False or col_count != num_vars:
#                        raise SaveError("""Can not save (append) to table %s. Variables do not match columns. 
#                                            vars:%s, columns:%s""" % (opt['dataset'], opt['_variables'], table_columns))
#                    
                    try:
                        #while rows are available get variables values 
                        #and insert into table
                        #TODO: currently committing after every insert, 
                        #see if possible to commit after no more rows available
                        while True:
                            row = (yield)
                            inserts = ''
                            
                            if opt['update'] == True:
                                inserts = ','.join(['%s=%s' % (var.name, _conv_var(var, value, opt)) 
                                                    for var, value in opt['_variables'].pair_filter(row)])
                            else:
                                inserts = ''.join(['(', 
                                                   ','.join([_conv_var(var, value, opt) for var, value in opt['_variables'].pair_filter(row)]),
                                                   ')'])
                            
                            if opt['update'] == True:
                                where = _get_where()
                                
                                i = "UPDATE %s Set %s WHERE %s" % (opt['dataset'], inserts, where)
                            elif opt['replace']:
                                i = "REPLACE INTO %s VALUES %s" % (opt['dataset'], inserts)   
                            else:
                                i = "INSERT INTO %s VALUES %s" % (opt['dataset'], inserts)
                            try:
                                c.execute(i)
                            except:
                                print i
                                raise
                            
                            
                                        
                    except (GeneratorExit, StopIteration):
                        cnxn.commit()
                    
#                    try:
#                        #while rows are available get variables values 
#                        #and insert into table
#                        #TODO: currently committing after every insert, 
#                        #see if possible to commit after no more rows available
#                        values = []
#                        while True:
#                            row = (yield)
#                            values.append(''.join(['(', 
#                                                   ','.join([_conv_var(var, value, opt) for var, value in opt['_variables'].pair_filter(row)]),
#                                                   ')']))
#                            
#                            
#                            if opt['update'] == True:
#                                inserts = ','.join(['%s=%s' % (var.name, _conv_var(var, value, opt)) 
#                                                    for var, value in opt['_variables'].pair_filter(row)])
#                            else:
#                                inserts = ''.join(['(', 
#                                                   ','.join([_conv_var(var, value, opt) for var, value in opt['_variables'].pair_filter(row)]),
#                                                   ')'])
#                            
#                            if opt['update'] == True:
#                                where = _get_where()
#                                
#                                i = "UPDATE %s Set %s WHERE %s" % (opt['dataset'], inserts, where)
#                            elif opt['replace']:
#                                i = "REPLACE INTO %s VALUES %s" % (opt['dataset'], inserts)   
#                            else:
#                                i = "INSERT INTO %s VALUES %s" % (opt['dataset'], inserts)
#                            
#                                        
#                    except (GeneratorExit, StopIteration):
#                        try:
#                            _vars = str(tuple([var.name for var in opt['_variables']]))
#                            i = 'INSERT INTO %s %s VALUES %s' % (opt['dataset'], _vars, ','.join(values))
#                            if opt['update']:
#                                'ON DUPLICATE KEY UPDATE'
#                            c.execute(i)
#                        except:
#                            raise
#                        
#                        cnxn.commit()
                    
register(MySQLOdbcHandler())