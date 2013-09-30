#!/usr/bin/python

""" Defines the backend connection class for basic SQL based databases. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

# define version information (major,minor,maintanence)
__depends__        = []
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import cPickle
import datetime
import logging
import threading
import time

import projex.iters
import projex.errors
import projex.text
import projex.rest
from projex.decorators import abstractmethod

import orb
from orb                 import errors, Orb, settings
from orb.common          import ColumnType, SelectionMode
from orb.connection      import Connection,\
                                DatabaseOptions,\
                                SchemaEngine,\
                                ColumnEngine
from orb.transaction     import Transaction
from orb.table           import Table
from orb.column          import Column
from orb.join            import Join
from orb.recordset       import RecordSet
from orb.query           import Query as Q, QueryCompound
from orb.common          import CallbackType

logger = logging.getLogger(__name__)

#----------------------------------------------------------------------
#                       DEFAULT SQL COMMANDS
#----------------------------------------------------------------------

DEFAULT_COMMON_CMDS = {
}

DEFAULT_SCHEMA_CMDS = {
'alter':
    """
    ALTER TABLE {table} {columns}
    """,
'aggregate':
    """
    LEFT OUTER JOIN {table} as {aggregate} ON {where}
    """,
'aggr_count':
    """
    COUNT(DISTINCT {table}.{colname})
    """,
'constraint_pkey':
    """
    CONSTRAINT {table} PRIMARY KEY ({columns})
    """,
'count':
    """
    SELECT COUNT(*) AS count FROM ({select_command}) AS records;
    """,
'create':
    """
    CREATE TABLE {table} ({columns}{constraints});
    """,
'create_inherited':
    """
    CREATE TABLE {table} (
        {inherit_id} INTEGER NOT NULL REFERENCES {inherits}{columns}{constraints}
    );
    """,
'delete':
    """
    DELETE FROM {table}
    WHERE {where};
    """,
'disable_internals':
    """
    SET unique_checks=0;
    SET foreign_key_checks=0;
    """,
'disable_table_internals':
    """
    ALTER TABLE {table} DISABLE KEYS;
    """,
'enable_table_internals':
    """
    ALTER TABLE {table} ENABLE KEYS;
    """,
'enable_internals':
    """
    SET unique_checks=1;
    SET foreign_key_checks=1;
    """,
'inherit_id':
    """
    __inherits__
    """,
'insert':
    """
    INSERT INTO {table}
    ({columns})
    VALUES
    {values};
    """,
'inner_join':
    """
    LEFT JOIN {table} ON {where}
    """,
'outer_join':
    """
    LEFT OUTER JOIN {table} ON {where}
    """,
'next_id':
    """
    SELECT _id+1 AS next_id FROM {table} ORDER BY _id DESC LIMIT 1;
    """,
'primary_id':
    """
    _id
    """,
'select':
    """
    SELECT {select_options} {columns}
    FROM {tables}{joins}{where}{group_by}{having}{lookup_options};
    """,
'truncate':
    """
    TRUNCATE {table};
    """,
'update':
    """
    UPDATE {table}
    SET {values}
    WHERE {where};
    """
}

DEFAULT_COLUMN_CMDS = {
'add':
    """
    ADD COLUMN {column} {type}{maxlen}{flags}
    """,
'add_ref':
    """
    ADD COLUMN {column} {type}{maxlen}{flags} REFERENCES {reference}
    """,
'create':
    """
    {column} {type}{maxlen}{flags}
    """,
'create_ref':
    """
    {column} {type}{maxlen}{flags} REFERENCES {reference}
    """,
'aggr_count':
    """
    COUNT(DISTINCT {table}.{colname})
    """,

# flag commands
Column.Flags.Required:      'NOT NULL',
Column.Flags.Unique:        'UNIQUE',
Column.Flags.AutoIncrement: 'AUTO_INCREMENT',

# operator options
'Is':                   '=',
'IsNot':                '!=',
'LessThan':             '<',
'Before':               '<',
'LessThanOrEqual':      '<=',
'GreaterThanOrEqual':   '>=',
'GreaterThan':          '>',
'After':                '>',
'Matches':              '~',
'DoesNotMatch':         '!~',
'ContainsSensitive':    'LIKE',
'ContainsInsensitive':  'ILIKE',
'IsIn':                 'IN',
'IsNotIn':              'NOT IN',

# function options
'Lower': 'lower({0})',
'Upper': 'upper({0})',
'Abs': 'abs({0}',
}
DEFAULT_COLUMN_CMDS.update(DEFAULT_COMMON_CMDS)

DEFAULT_TYPE_MAP = {
    ColumnType.Bool:        'BOOL',
        
    ColumnType.Decimal:     'DECIMAL UNSIGNED',
    ColumnType.Double:      'DOUBLE UNSIGNED',
    ColumnType.Integer:     'INT UNSIGNED',
    ColumnType.Enum:        'INT UNSIGNED',
    ColumnType.BigInt:      'BIGINT UNSIGNED',
    
    ColumnType.ForeignKey:  'BIGINT UNSIGNED',
    
    ColumnType.Datetime:             'DATETIME',
    ColumnType.Date:                 'DATE',
    ColumnType.Time:                 'TIME',
    ColumnType.DatetimeWithTimezone: 'TIMESTAMP',
        
    ColumnType.String:      'VARCHAR',
    ColumnType.Color:       'VARCHAR',
    ColumnType.Email:       'VARCHAR',
    ColumnType.Password:    'VARCHAR',
    ColumnType.Url:         'VARCHAR',
    ColumnType.Filepath:    'VARCHAR',
    ColumnType.Directory:   'VARCHAR',
    ColumnType.Text:        'TEXT',
    ColumnType.Xml:         'TEXT',
    ColumnType.Html:        'TEXT',
    ColumnType.Dict:        'TEXT',
        
    ColumnType.ByteArray:   'VARBINARY',
    ColumnType.Pickle:      'BLOB',
    ColumnType.Dict:        'BLOB',
    ColumnType.Image:       'BLOB'
}

DEFAULT_LENGTHS = {
    ColumnType.String:    256,
    ColumnType.Color:     25,
    ColumnType.Email:     256,
    ColumnType.Password:  256,
    ColumnType.Url:       500,
    ColumnType.Filepath:  500,
    ColumnType.Directory: 500
}


#----------------------------------------------------------------------
#                           CLASS DEFINITIONS
#----------------------------------------------------------------------

class SqlColumnEngine(ColumnEngine):
    def __init__(self, backend, sqltype, wrapper='`', cmds=None):
        super(SqlColumnEngine, self).__init__(backend)
        
        # define custom properties
        self._sqltype = sqltype
        
        # define flag sql information
        self.setStringWrapper(wrapper)
        if cmds is not None:
            for key, cmd in cmds.items():
                self.setCommand(key, cmd)
    
    def addCommand(self, column):
        """
        Generates the SQL command required for adding this column to the
        table.
        
        :param      column | <orb.Column>
        
        :return     <str>
        """
        cmd = ''
        if column.testFlag(Column.Flags.Primary):
            cmd = self.command('add_primary')
        elif column.reference():
            cmd = self.command('add_ref')
        if not cmd:
            cmd = self.command('add')
        
        return cmd.format(**self.options(column))
    
    def createCommand(self, column):
        """
        Creates the SQL commands for generating the given column.
        
        :param      column | <orb.Column>
        
        :return     <str>
        """
        cmd = ''
        if column.testFlag(Column.Flags.Primary):
            cmd = self.command('create_primary')
        elif column.reference():
            cmd = self.command('create_ref')
        if not cmd:
            cmd = self.command('create')
        
        return cmd.format(**self.options(column))
    
    def options(self, column):
        """
        Generates the options required for this column.
        
        :return     <dict>
        """
        opts = {}
        opts['column'] = self.wrapString(column.fieldName())
        opts['type'] = self._sqltype
        
        if column.reference():
            refmodel = column.referenceModel()
            if refmodel:
                refname = self.wrapString(refmodel.schema().tableName())
                opts['reference'] = refname
            else:
                raise errors.TableNotFoundError(column.reference())
        else:
            opts['reference'] = ''
        
        # assign the max length value
        maxlen = column.maxlength()
        if not maxlen:
            maxlen = DEFAULT_LENGTHS.get(column.columnType())
        if maxlen:
            opts['maxlen'] = '({})'.format(maxlen)
        else:
            opts['maxlen'] = ''
        
        # format the flag information
        flag_opts = []
        for flag in column.iterFlags():
            cmd = self.command(flag)
            if cmd:
                flag_opts.append(cmd.format(**opts))
        
        if flag_opts:
            opts['flags'] = ' ' + ' '.join(flag_opts)
        else:
            opts['flags'] = ''
        
        return opts
    
    def queryCommand(self,
                     schema,
                     column,
                     op,
                     value,
                     offset='',
                     caseSensitive=False,
                     functions=None,
                     setup=None):
        """
        Converts the inputed column, operator and value to a query statement.
        
        :param      columns       | <orb.TableSchema>
                    op            | <orb.Column.Op>
                    value         | <variant>
                    offset        | <str>
                    caseSensitive | <bool>
                    functions     | [<str>, ..] || None
                    setup         | <dict> || None
        
        :return     <str> cmd, <dict> data
        """
        if setup is None:
            setup = {}
        if functions is None:
            functions = []
        
        data = {}
        
        if column.isJoined():
            schema_name = setup['column_aliases'][column]
            column = column.joiner()[0]
            schema = column.schema()
            sqlfield = self.wrapString(schema_name, column.fieldName()) + offset
            
        elif column.isAggregate():
            aggr = column.aggregate()
            
            cmd = self.command('aggr_{0}'.format(aggr.type()))
            if not cmd:
                raise errors.UnsupportedWhereAggregate(aggr.type())
            
            col_schema = aggr.table().schema()
            
            opts = {}
            opts['table'] = self.wrapString(setup['column_aliases'][column])
            if col_schema.inherits() and not self.backend().isObjectOriented():
                opts['colname'] = self.wrapString('__inherits__')
            else:
                pcol = col_schema.primaryColumns()[0]
                opts['colname'] = self.wrapString(pcol.fieldName())
            
            sqlfield = cmd.format(**opts)
        
        else:
            schema_name = column.schema().tableName()
            sqlfield = self.wrapString(schema_name, column.fieldName()) + offset
        
        # join functions together for the sqlfield
        for function in functions:
            func_cmd = self.command(function)
            if func_cmd:
                sqlfield = func_cmd.format(sqlfield)
        
        value    = self.wrap(column, value)
        field    = column.fieldName()
        vkey     = self.genkey('query_' + field)
        
        # generate the between query
        if op == Q.Op.Between:
            cmd = '(%({0})s <= {1} AND {1} <= %({0}_b)s)'
            cmd = cmd.format(vkey, sqlfield)
            
            data[vkey] = value[0]
            data[vkey+'_b'] = value[1]
            return cmd, data
        
        # generate a contain query
        elif op in (Q.Op.Contains, Q.Op.DoesNotContain):
            if caseSensitive:
                sqlop = self.command('ContainsSensitive')
            else:
                sqlop = self.command('ContainsInsensitive')
            
            # perform binary comparison
            if ColumnType.base(column.columnType()) in (ColumnType.Integer,
                                                        ColumnType.BigInt,
                                                        ColumnType.Enum):
                if op == Q.Op.Contains:
                    cmd = '({0} & %({2})s) != 0'
                else:
                    cmd = '({0} & %({2})s) == 0'
            else:
                if op == Q.Op.Contains:
                    cmd = '{0} {1} %({2})s'
                else:
                    cmd = '{0} NOT {1} %({2})s'
                
                encoded = projex.text.encoded(value, column.encoding())
                value = '%{0}%'.format(encoded.replace('*', '%'))
            
            data[vkey] = value
            return cmd.format(sqlfield, sqlop, vkey), data
        
        # generate a startswith/endswith query
        elif op in (Q.Op.Startswith, Q.Op.Endswith):
            encoded = projex.text.encoded(value, column.encoding())
            if op == Q.Op.Startswith:
                value = '^{0}.*$'.format(encoded)
            else:
                value = '^.*{0}$'.format(encoded)
            
            sqlop = self.command('Matches')
            data[vkey] = value
            return '{0} {1} %({2})s'.format(sqlfield, sqlop, vkey), data
        
        # generate a options query
        elif op in (Q.Op.IsIn, Q.Op.IsNotIn):
            value = tuple(value)
            if not value:
                return '__RECORDS_ARE_BLANK__', {}
        
        # generate a basic query
        sqlop = self.command(Q.Op[op])
        if not sqlop:
            raise errors.DatabaseError('Unknown query operator: %s', op)
        
        data[vkey] = value
        return '{0} {1} %({2})s'.format(sqlfield, sqlop, vkey), data
    
    def setSqltype(self, sqltype):
        """
        Sets the SQL type associated with this engine.
        
        :param      sqltype | <str>
        """
        self._sqltype = sqltype
        
    def sqltype(self):
        """
        Returns the SQL type associated with this engine.
        
        :return     <str>
        """
        return self._sqltype
    
#----------------------------------------------------------------------

class SqlSchemaEngine(SchemaEngine):
    def __init__(self, backend, wrapper='`', cmds=None):
        super(SqlSchemaEngine, self).__init__(backend, wrapper=wrapper)
        
        # define sql commands
        if cmds is not None:
            for key, cmd in cmds.items():
                self.setCommand(key, cmd)
        
    def alterCommand(self, schema, columns=None):
        """
        Generates the alter table command.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        # load the columns
        if columns is None:
            columns = schema.columns(recurse=False,
                                     includeProxies=False,
                                     includeJoined=False,
                                     includeAggregates=False)
        
        # generate the alter command
        cols = []
        db = self.backend().database()
        columns.sort(key = lambda x: x.name())
        for col in columns:
            engine = col.engine(db)
            cols.append(engine.addCommand(col))
        
        # generate options
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        opts['columns'] = '\n\t' + ',\n\t'.join(cols)
        
        return self.command('alter').format(**opts), {}
    
    def countCommand(self, schemas, **options):
        """
        Returns the command that will be used to calculate the count that
        will be returned for the given query options.
        
        :param      schemas   | [<orb.TableSchema>, ..]
                    **options | database options
        
        :return     <str> sql, <dict> data
        """
        # include any required columns
        colnames = [schemas[0].primaryColumns()[0].name()]
        
        if 'where' in options:
            where = options['where']
        elif 'lookup' in options:
            where = options['lookup'].where
        else:
            where = None
        
        # join any columns from the query
        if where:
            for column in where.columns(schemas[0]):
                if column.isMemberOf(schemas):
                    colnames.append(column.name())
        
        # generate the options
        if 'lookup' in options:
            options['lookup'].columns = colnames
        elif not 'columns' in options:
            options['columns'] = colnames
        
        selcmd, data = self.selectCommand(schemas, **options)
        
        opts = {}
        opts['select_command'] = selcmd.rstrip(';')
        
        return self.command('count').format(**opts), data
    
    def columnsCommand(self, schema):
        """
        Returns the command for the inputed schema to lookup its
        columns from the database.
        
        :return     <str> sql, <dict> data
        """
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        data = {}
        data['table'] = schema.tableName()
        return self.command('existing_columns').format(**opts), data
    
    def createCommand(self, schema):
        """
        Generates the table creation command.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        # generate the column query command
        cols = []
        db = self.backend().database()
        columns = schema.columns(recurse=False,
                                 includeProxies=False,
                                 includeJoined=False,
                                 includeAggregates=False)
        columns.sort(key=lambda x: x.name())
        for col in columns:
            col_engine = col.engine(db)
            cols.append(col_engine.createCommand(col))
        
        # generate the constraints command
        constraints = []
        if not schema.inherits():
            pcols = schema.primaryColumns()
            pkeys = map(lambda x: self.wrapString(x.fieldName()), pcols)
            
            cmd = self.command('constraint_pkey')
            if cmd:
                opts = {}
                opts['table']   = self.wrapString(schema.tableName() + '_pkey')
                opts['columns'] = ','.join(pkeys)
                constraints.append(cmd.format(**opts))
        
        # generate options
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        if cols:
            opts['columns'] = '\n\t' + ',\n\t'.join(cols)
        else:
            opts['columns'] = ''
        
        if constraints:
            opts['constraints'] = ',\n\t' + ',\n\t'.join(constraints)
        else:
            opts['constraints'] = ''
        opts['username'] = self.wrapString(db.username())
        
        if schema.inherits():
            inherited_schema = schema.ancestor()
            if not inherited_schema:
                raise errors.TableNotFoundError(schema.inherits())
            
            opts['inherit_id'] = self.wrapString(self.command('inherit_id'))
            opts['inherits'] = self.wrapString(inherited_schema.tableName())
            
            if opts['columns']:
                opts['columns'] = ',' + opts['columns']
            
            return self.command('create_inherited').format(**opts), {}
        else:
            return self.command('create').format(**opts), {}
    
    def existsCommand(self, schema):
        """
        Returns the command that will determine whether or not the schema
        exists in the database.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        data = {}
        data['table'] = schema.tableName()
        return self.command('exists').format(**opts), data
    
    def disableInternalsCommand(self, schema):
        """
        Generates the disable internals command for this schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        
        return self.command('disable_table_internals').format(**opts), {}
    
    def enableInternalsCommand(self, schema):
        """
        Generates the enable internals command for this schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        
        return self.command('enable_table_internals').format(**opts), {}
    
    def insertCommand(self,
                      schema,
                      records,
                      columns=None,
                      autoincrement=True,
                      first=True,
                      setup=None):
        """
        Generates the insertion command for this engine.
        
        :param      schema  | <orb.TableSchema>
                    records | [<orb.Table>, ..]
        
        :return     <str> command, <dict> data
        """
        # generate the values
        if setup is None:
            setup = {}
        
        fields = []
        values = []
        data = {}
        engines = {}
        schema_columns = []
        colnames = []
        cmd = ''
        is_base = True
        
        # map the column and field information
        db = self.backend().database()
        is_oo = self.backend().isObjectOriented()
        
        # insert ancestor records
        if not is_oo:
            ancest = schema.ancestor()
            if ancest:
                is_base = False
                cmd, data = self.insertCommand(ancest,
                                               records,
                                               columns=columns,
                                               autoincrement=autoincrement,
                                               first=False,
                                               setup=setup)
                
            elif autoincrement and not first:
                if setup.get(schema, {}).get('next_id') is None:
                    next_id_cmd = self.command('next_id')
                    opts = {}
                    opts['table'] = self.wrapString(schema.tableName())
                    
                    result = self.backend().execute(next_id_cmd.format(**opts))
                    setup.setdefault(schema, {})
                    if result:
                        setup[schema]['next_id'] = result[0]['next_id']
                    else:
                        setup[schema]['next_id'] = 1
                
                for r, record in enumerate(records):
                    if type(record) == dict:
                        record['_id'] = setup[schema]['next_id']
                    else:
                        rdata = {'_id': setup[schema]['next_id']}
                        record._updateFromDatabase(rdata)
                    setup[schema]['next_id'] += 1
                
                autoincrement=False
        
        # insert individual column information
        for column in schema.columns(recurse=is_oo,
                                     includeProxies=False,
                                     includeJoined=False,
                                     includeAggregates=False):
            
            # ignore auto-incrementing columns
            if autoincrement and column.testFlag(Column.Flags.AutoIncrement):
                continue
            
            colname = column.name()
            if columns is None or colname in columns:
                field = column.fieldName()
                fields.append(field)
                colnames.append(colname)
                schema_columns.append(column)
                engines[colname] = column.engine(db)
        
        if not fields:
            return '', {}
        
        # enumerates the records
        for r, record in enumerate(records):
            if Table.recordcheck(record):
                record = record.recordValues(autoInflate=False)
            
            field_values = []
            for i, colname in enumerate(colnames):
                column = schema_columns[i]
                if autoincrement and column.testFlag(Column.Flags.AutoIncrement):
                    continue
                    
                field = fields[i]
                key = self.genkey(field)
                field_values.append('%({0})s'.format(key))
                value = record.get(colname)
                data[key] = engines[colname].wrap(column, value)
            
            if not is_base:
                key = self.genkey('__inherits__')
                if not '__inherits__' in fields:
                    fields.append('__inherits__')
                
                field_values.append('%({0})s'.format(key))
                data[key] = record.get('_id')
            
            values.append('(' + ','.join(field_values) + ')')
        
        # generate options
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        opts['columns'] = ','.join(map(self.wrapString, fields))
        opts['values'] = ',\n    '.join(values)
        
        out_cmd = self.command('insert').format(**opts)
        if cmd:
            out_cmd = cmd + '\n' + out_cmd
        
        return out_cmd, data
    
    def insertedCommand(self, schema, count=1):
        """
        Returns the last inserted rows from the schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> sql, <dict> data
        """
        if self.backend().isObjectOriented() or not schema.inherits():
            pcols = schema.primaryColumns()
            if not pcols:
                raise errors.PrimaryKeyNotDefinedError()
            pcol = pcols[0].fieldName()
        
        elif schema.inherits():
            pcol = '__inherits__'
        
        # generate options for command
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        opts['column'] = self.wrapString(pcol)
        opts['count'] = count
        
        return self.command('inserted_keys').format(**opts), {}
    
    def joinTraversal(self, schemas, column, traverse, setup=None):
        """
        Joins the schemas from a traversal together for the setup.
        
        :param      schemas  | [<orb.TableSchema>, ..]
                    column   | <orb.Column> | source column
                    traverse | [<orb.TableSchema>, ..]
                    setup    | <dict> || None
        """
        if not (traverse and schemas):
            return
        
        if setup is None:
            setup = {}
        
        innerjoin = self.command('inner_join')
        is_oo = self.backend().isObjectOriented()
        path = []
        traverse.reverse()
        traverse.append(column)
        
        last_key = self.wrapString(traverse[0].schema().tableName(),
                                   traverse[0].fieldName())
                                   
        for curr in traverse[1:]:
            if is_oo:
                cschema = curr.firstMemberSchema(schemas)
            else:
                cschema = curr.schema()
            
            pkeycols = cschema.primaryColumns()
            if len(pkeycols) == 1:
                curr_key = self.wrapString(cschema.tableName(),
                                           pkeycols[0].fieldName())
            else:
                pdata = []
                for pkeycol in pkeycols:
                    pdata.append(self.wrapString(cschema.tableName(),
                                                 pkeycol.fieldName()))
                curr_key = '('+','.join(pdata)+')'
            
            opts = {}
            opts['table'] = self.wrapString(cschema.tableName())
            opts['where'] = '{0}={1}'.format(last_key, curr_key)
            joincmd = innerjoin.format(**opts)
            
            setup.setdefault('joins', [])
            setup.setdefault('join_schemas', [])
            setup['joins'].append('\n'+joincmd)
            setup['join_schemas'].append(cschema)
            
            last_key = self.wrapString(cschema.tableName(), curr.fieldName())
    
    def queryCommand(self, schemas, query, setup=None):
        """
        Generates the query command for the given information.
        
        :param      schemas | <orb.TableSchema>
                    query   | <orb.Query>
        
        :return     <str> command, <dict> data
        """
        if setup is None:
            setup = {}
        
        commands    = []
        data        = {}
        db          = self.backend().database()
        
        traverse    = []
        column      = query.column(schemas[0], traversal=traverse)
        op          = query.operatorType()
        value       = query.value()
        is_oo       = self.backend().isObjectOriented()
        innerjoin   = self.command('inner_join')
        
        # add traversal paths to the command
        self.joinTraversal(schemas, column, traverse, setup)
        
        # determine if this query is a join query
        qschemas = query.schemas()
        if len(qschemas) > 1:
            joined = set(qschemas).difference(schemas+setup['join_schemas'])
            if joined:
                qschema = list(joined)[0]
                qwhere, _, qdata = self.whereCommand(schemas + [qschema],
                                                  query,
                                                  setup)
                
                if qwhere and \
                   not qschema in setup['join_query_order'] and \
                   not qschema in setup['orig_schemas']:
                    setup['join_schemas'].append(qschema)
                    setup['join_query_order'].append(qschema)
                    setup['join_queries'].setdefault(qschema, [])
                    setup['join_queries'][qschema].append(qwhere)
                    setup['data'].update(qdata)
                    
                    return '', {}
        
        if not column:
            raise errors.ColumnNotFoundWarning(query.columnName())
        
        # lookup primary key information
        if type(column) == tuple:
            if not type(value) in (list, tuple):
                value = (value,)
            
            if not len(column) == len(value):
                raise errors.InvalidQueryError(query)
        else:
            column = (column,)
            value  = (value,)
        
        if query.isOffset():
            offset, offset_data = self.queryOffset(schemas, query, setup)
            data.update(offset_data)
        else:
            offset = ''
        
        for column, value in dict(zip(column, value)).items():
            engine = column.engine(db)
            if is_oo:
                schema = column.firstMemberSchema(schemas)
            else:
                schema = column.schema()
            
            field  = column.fieldName()
            sqlfield = self.wrapString(schema.tableName(), field)
            
            #-----------------------------------------------------------------
            # pre-process value options
            #-----------------------------------------------------------------
            # ignore query
            if Q.typecheck(value):
                pass
            
            # lookup all instances of a record
            elif value == Q.ALL:
                continue
            
            # lookup all NOT NULL instances of a record
            elif value == Q.NOT_EMPTY or \
                 (value == None and op == Q.Op.IsNot):
                commands.append('{0} IS NOT NULL'.format(sqlfield))
                continue
            
            # lookup all NULL instances
            elif value == Q.EMPTY or (value == None and op == Q.Op.Is):
                commands.append('{0} IS NULL'.format(sqlfield))
                continue
            
            # process the value
            else:
                value = engine.wrap(column, value)
            
            vcmd, vdata = engine.queryCommand(schema,
                                              column,
                                              op,
                                              value,
                                              offset=offset,
                                            caseSensitive=query.caseSensitive(),
                                            functions=query.functionNames(),
                                            setup=setup)
            if vcmd:
                commands.append(vcmd)
                data.update(vdata)
        
        # strip out any query reference information
        cmd = ' AND '.join(commands)
        for key, val in data.items():
            if Q.typecheck(val):
                qcmd, qdata = self.queryValue(schemas, val, setup)
                cmd = cmd.replace('%({0})s'.format(key), qcmd)
                data.pop(key)
                data.update(qdata)
        
        return cmd, data
        
    def removeCommand(self, schema, records):
        """
        Generates the command for removing the inputed records from the
        database.
        
        :param      schema  | <orb.TableSchema>
                    records | [<orb.Table>, ..]
        
        :return     <str> command, <dict> data
        """
        pcols = schema.primaryColumns()
        data = {}
        pkeys = []
        base_cmd = ''
        base_data = {}
        is_oo = self.backend().isObjectOriented()
        
        # remove from non-object-oriented databases
        if not is_oo and schema.inherits():
            ancest = schema.ancestor()
            if ancest:
                base_cmd, base_data = self.removeCommand(ancest, records)
            
            pcolnames = self.wrapString('__inherits__')
        
        # remove base records
        elif len(pcols) == 1:
            pcolnames = self.wrapString(pcols[0].schema().tableName(),
                                        pcols[0].fieldName())
        
        else:
            mapper = lambda x: self.wrapString(x.schema().tableName(), 
                                               x.fieldName())
            pcolnames = '('+','.join(map(mapper, pcols)) + ')'
        
        # extract the primary keys from the given record set
        if RecordSet.typecheck(records):
            records = records.primaryKeys()
        
        # collect the primary keys for removal
        for record in records:
            if Table.recordcheck(record):
                pkey = record.primaryKey()
                if pkey is None:
                    continue
            else:
                pkey = record
            
            datakey = self.genkey('pkey')
            data[datakey] = pkey
            pkeys.append('%({0})s'.format(datakey))
        
        # generate command options
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        opts['where'] = '{0} IN ({1})'.format(pcolnames, ','.join(pkeys))
        
        cmd = self.command('delete').format(**opts)
        
        if base_cmd:
            data.update(base_data)
            return base_cmd + '\n' + cmd, data
        else:
            return cmd, data
        
    def selectCommand(self, schemas, **options):
        """
        Generates the selection command for this engine.
        
        :param      schemas | [<orb.TableSchema>, ..]
        
        :return     <str> command, <dict> data
        """
        # initialize data collections
        setup = options.get('setup', {})
        data  = setup.get('data', {})
        
        fields = []
        
        setup.setdefault('data', data)
        setup.setdefault('aliases', {})
        setup.setdefault('orig_schemas', schemas[:])
        setup.setdefault('where', '')
        setup.setdefault('having', '')
        setup.setdefault('join_queries', {})
        setup.setdefault('join_query_order', [])
        setup.setdefault('lookup', [])
        setup.setdefault('column_aliases', {})
        setup.setdefault('group_by', [])
        setup.setdefault('joins', [])
        setup.setdefault('join_schemas', [])
        
        # use provided options
        datamapper  = options.get('datamapper', {})
        columns     = options.get('columns')
        lookup      = options.get('lookup', orb.LookupOptions(**options))
        is_oo       = self.backend().isObjectOriented()
        schemas     = schemas[:]
        aggregate_aliases = {}
        aggregate_cache = {}
        
        innerjoin   = self.command('inner_join')
        outerjoin   = self.command('outer_join')
        aggrjoin    = self.command('aggregate')
        
        # create the grouping keys
        # include any inheritance
        if not is_oo:
            bases = []
            pkey = self.command('primary_id')
            inherit = self.command('inherit_id')
            for schema in schemas[:]:
                ancestry = schema.ancestry()
                ancestry.append(schema)
                for i in range(1, len(ancestry)):
                    if i == 1:
                        a = self.wrapString(ancestry[i-1].tableName(), pkey)
                    else:
                        a = self.wrapString(ancestry[i-1].tableName(), inherit)
                    
                    b = self.wrapString(ancestry[i].tableName(), inherit)
                    
                    opts = {}
                    opts['table'] = self.wrapString(ancestry[i-1].tableName())
                    opts['where'] = '{0}={1}'.format(a, b)
                    
                    setup['joins'].append('\n'+innerjoin.format(**opts))
                    if not ancestry[i-1] in setup['join_schemas']:
                        setup['join_schemas'].append(ancestry[i-1])
        
        # determine which coluns to lookup
        if columns is None:
            columns = [c for s in schemas \
                         for c in s.columns(includeProxies=False)]
            if lookup.columns:
                columns = filter(lambda x: x.name() in lookup.columns, columns)
                
        # lookup joined & aggregate columns
        use_group_by = False
        for column in columns:
            joiner    = column.joiner()
            aggregate = column.aggregate()
            
            # include joiner
            if joiner:
                adv_schema = joiner[0].schema()
                adv_where = joiner[1]
            
            # include aggregate
            elif aggregate:
                adv_schema = aggregate.table().schema()
                adv_where = aggregate.lookupOptions().where
            
            # ignore this column
            else:
                continue
            
            aggr_key = (adv_schema.name(), hash(adv_where))
            if aggr_key in aggregate_cache:
                adv_key = aggregate_cache[aggr_key]
                setup['column_aliases'][column] = adv_key
                continue
            else:
                adv_key = column.fieldName() + '_aggr'
                aggregate_cache[aggr_key] = adv_key
                setup['column_aliases'][column] = adv_key
            
            use_group_by = True
            where_cmd, _, where_data = self.whereCommand([adv_schema],
                                                      adv_where,
                                                      setup)
            
            where_cmd = where_cmd.replace(adv_schema.tableName(), adv_key)
            
            opts = {}
            opts['table'] = self.wrapString(adv_schema.tableName())
            opts['aggregate'] = self.wrapString(adv_key)
            opts['where'] = where_cmd
            
            setup['joins'].append('\n'+aggrjoin.format(**opts))
            data.update(where_data)
            
        # generare where SQL
        if lookup.where is not None:
            qwhere, qhaving, qdata = self.whereCommand(schemas,
                                            lookup.where,
                                            setup)
            
            # add any traversal queries
            for schema in setup['join_query_order']:
                queries = setup['join_queries'][schema]
                opts = {}
                opts['table'] = self.wrapString(schema.tableName())
                opts['where'] = ' AND '.join(queries)
                
                setup['joins'].append('\n'+innerjoin.format(**opts))
            
            if qwhere:
                setup['where'] = '\nWHERE {0}'.format(qwhere)
                data.update(qdata)
            
            if qhaving:
                setup['having'] = '\nHAVING {0}'.format(qhaving)
                data.update(qdata)
            
        # generate default order
        if lookup.order is None:
            lookup.order = schemas[0].defaultOrder()
        
        # generate order SQL
        if lookup.order is not None:
            order_cmds = []
            for colname, direction in lookup.order:
                # look up the first matching column
                scolumn = None
                straverse = []
                for schema in schemas:
                    traverse = []
                    column = schema.column(colname, traversal=traverse)
                    if column:
                        scolumn = column
                        straverse = traverse
                        break
                
                # add the schema sorted column to the system
                if not scolumn:
                    continue
                
                # join in the columns if necessary
                self.joinTraversal(schemas, scolumn, straverse, setup)
                
                if is_oo:
                    schema = scolumn.firstMemberSchema(schemas)
                else:
                    schema = scolumn.schema()
                
                if scolumn.isAggregate() or scolumn.isJoined():
                    key = schema.tableName() + '_' + scolumn.fieldName()
                    key = self.wrapString(key)
                else:
                    key = self.wrapString(schema.tableName(),
                                          scolumn.fieldName())
                    setup['group_by'].append(key)
                
                if lookup.distinct and not key in fields:
                    fields.append(key)
                
                order_cmds.append('{0} {1}'.format(key, direction.upper()))
            
            if order_cmds:
                cmd = '\nORDER BY {0}'.format(','.join(order_cmds))
                setup['lookup'].append(cmd)
        
        # generate limit SQL
        if lookup.limit is not None:
            setup['lookup'].append('\nLIMIT {0}'.format(lookup.limit))
        
        # generate offset SQL
        if lookup.start is not None:
            setup['lookup'].append('\nOFFSET {0}'.format(lookup.start))
        
        # define selection options
        select_options = []
        if lookup.distinct:
            select_options.append('DISTINCT')
        
        # generate the fields to lookup
        for column in columns:
            if is_oo:
                schema = column.firstMemberSchema(schemas)
            else:
                schema = column.schema()
            
            use_alias = False
            
            # include joins for this query
            if column.isJoined():
                src = column.joiner()[0]
                src_table = setup['column_aliases'][column]
                src_field = src.fieldName()
                src = self.wrapString(src_table, src_field)
                setup['group_by'].append(src)
            
            # include aggregates for this query
            elif column.isAggregate():
                aggr = column.aggregate()
                src_table = setup['column_aliases'][column]
                
                opts = {}
                opts['table'] = self.wrapString(src_table)
                if schema.inherits() and not is_oo:
                    opts['colname'] = self.wrapString('__inherits__')
                else:
                    pcol = schema.primaryColumns()[0]
                    opts['colname'] = self.wrapString(pcol.fieldName())
                
                cmd = self.command('aggr_{0}'.format(aggr.type()))
                src = cmd.format(**opts)
                use_alias = True
            
            # include regular columns
            else:
                src_table = schema.tableName()
                src_field = column.fieldName()
                src = self.wrapString(src_table, src_field)
                setup['group_by'].append(src)
            
            target_key = schema.tableName() + '_' + column.fieldName()
            
            datamapper[target_key] = column
            opts = (src, self.wrapString(target_key))
            fields.append('{0} AS {1}'.format(*opts))
        
        # generate the SQL table names
        tables = map(lambda x: self.wrapString(x.tableName()), schemas)
        
        # generate options
        opts = {}
        opts['select_options'] = ' '.join(select_options)
        opts['tables'] = ','.join(tables)
        opts['columns'] = ','.join(fields)
        opts['joins'] = ''.join(setup['joins'])
        opts['where'] = setup['where']
        opts['having'] = setup['having']
        opts['lookup_options'] = ''.join(setup['lookup'])
        
        if use_group_by:
            opts['group_by'] = '\nGROUP BY ' + ','.join(setup['group_by'])
        else:
            opts['group_by'] = ''
        
        return self.command('select').format(**opts), data
    
    def updateCommand(self, schema, records, columns=None):
        """
        Updates the records for the given schema in the database.
        
        :param      schema  | <orb.TableSchema>
                    records | [<orb.Table>, ..]
        
        :return     <str> command, <data> dict
        """
        pcols = schema.primaryColumns()
        pkeys = map(lambda x: x.primaryKey(), records)
        is_oo = self.backend().isObjectOriented()
        
        data  = {}
        commands = []
        db = self.backend().database()
        updatecmd = self.command('update')
        
        for r, record in enumerate(records):
            if not record.isRecord():
                continue
            
            changes = record.changeset(columns=columns, includeProxies=False)
            
            if not changes:
                continue
            
            values = []
            where = []
            pkey = pkeys[r]
            if not type(pkey) in (list, tuple):
                pkey = (pkey,)
            
            # generate the where command
            if len(pkey) != len(pcols):
                raise errors.DatabaseError('Invalid primary key: %s' % pkey)
            
            elif len(pkey) == 1:
                if is_oo or not schema.inherits():
                    colcmd = '{0}=%({1})s'
                    tname = pcols[0].schema().tableName()
                    fname = pcols[0].fieldName()
                    field = self.wrapString(tname, fname)
                    datakey = self.genkey(fname)
                else:
                    colcmd = '{0}=%({1})s'
                    field = self.wrapString(self.command('inherit_id'))
                    datakey = self.genkey('inherits')
                
                cmd = colcmd.format(field, datakey)
                data[datakey] = pkey[0]
                where.append(cmd)
            
            else:
                for i, pcol in enumerate(pcols):
                    colcmd = '{0}=%({1})s'
                    tname = pcol.schema().tableName()
                    fname = pcol.fieldName()
                    datakey = self.genkey(fname)
                    cmd = colcmd.format(self.wrapString(tname, fname), datakey)
                    data[datakey] = pkey[i]
                    where.append(cmd)
            
            # generate the setting command
            for colname, change in changes.items():
                column = schema.column(colname, recurse=is_oo)
                if not column:
                    continue
                
                engine = column.engine(db)
                newval = engine.wrap(column, change[1])
                
                field = self.wrapString(column.fieldName())
                
                datakey = self.genkey('update_' + column.fieldName())
                data[datakey] = newval
                values.append('{0}=%({1})s'.format(field, datakey))
            
            if values:
                # generate formatting options
                opts = {}
                opts['table'] = self.wrapString(schema.tableName())
                opts['values'] = ', '.join(values)
                opts['where'] = ' AND '.join(where)
                
                commands.append(updatecmd.format(**opts))
        
        return '\n'.join(commands), data

    def truncateCommand(self, schema):
        """
        Generates the truncation command for this schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     <str> command, <dict> data
        """
        opts = {}
        opts['table'] = self.wrapString(schema.tableName())
        
        return self.command('truncate').format(**opts), {}

#----------------------------------------------------------------------

class SqlBase(Connection):
    """ 
    Creates a SQL based backend connection type for handling database
    connections to different SQL based databases.  This class can be subclassed
    to define different SQL connections.
    """
    
    def __init__(self,
                 database,
                 stringWrapper="`",
                 schemaCommands=None,
                 columnCommands=None,
                 typeMap=None,
                 schemaEngine=SqlSchemaEngine,
                 columnEngine=SqlColumnEngine):
        
        super(SqlBase, self).__init__(database)
        
        # define custom properties
        self._objectOriented = False
        self._insertBatchSize = 500
        self._thread_dbs = {}      # thread id, database conneciton
        
        # set standard properties
        self.setThreadEnabled(True)
        
        if schemaCommands is None:
            schemaCommands = DEFAULT_SCHEMA_CMDS
        if columnCommands is None:
            columnCommands = DEFAULT_COLUMN_CMDS
        if typeMap is None:
            typeMap = DEFAULT_TYPE_MAP
        
        # define default wrappers
        self.setEngine(schemaEngine(self,
                                    wrapper=stringWrapper,
                                    cmds=schemaCommands))
        
        for typ, sqltype in typeMap.items():
            col_engine = columnEngine(self,
                                      sqltype,
                                      wrapper=stringWrapper,
                                      cmds=columnCommands)
            self.setColumnEngine(typ, col_engine)
        
        # add any custom engines
        plug = type(self).__name__
        for typ, engine_type in orb.Orb.instance().customEngines(plug):
            col_engine = engine_type(self,
                                     wrapper=stringWrapper,
                                     cmds=columnCommands)
            self.setColumnEngine(typ, col_engine)

    #----------------------------------------------------------------------
    #                       PROTECTED METHODS
    #----------------------------------------------------------------------
    @abstractmethod()
    def _execute(self, 
                 command, 
                 data       = None,
                 autoCommit = True,
                 autoClose  = True,
                 returning  = True,
                 mapper     = dict):
        """
        Executes the inputed command into the current \
        connection cursor.
        
        :param      command    | <str>
                    data       | <dict> || None
                    autoCommit | <bool> | commit database changes immediately
                    autoClose  | <bool> | closes connections immediately
                    returning  | <bool>
                    mapper     | <variant>
                    retries    | <int>
        
        :return     [{<str> key: <variant>, ..}, ..]
        """
        return []
        
    @abstractmethod()
    def _open(self, db):
        """
        Handles simple, SQL specific connection creation.  This will not
        have to manage thread information as it is already managed within
        the main open method for the SQLBase class.
        
        :param      db | <orb.Database>
        
        :return     <variant> | backend specific database connection
        """
        return None
    
    @abstractmethod()
    def _interrupt(self, threadId, backendDb):
        """
        Interrupts the given backend database connection from a separate thread.
        
        :param      threadId   | <int>
                    backendDb | <variant> | backend specific database.
        """
        pass

    #----------------------------------------------------------------------
    #                       PUBLIC METHODS
    #----------------------------------------------------------------------

    def backendDb(self):
        """
        Returns the sqlite database for the current thread.
        
        :return     <variant> || None
        """
        tid = threading.current_thread().ident
        return self._thread_dbs.get(tid)
    
    def close(self):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        cid = threading.current_thread().ident
        for tid, thread_db in self._thread_dbs.items():
            if tid == cid:
                thread_db.close()
            else:
                self._interrupt(tid, thread_db)
        
        self._thread_dbs.clear()
        return True
    
    def count(self, table_or_join, lookup, options):
        """
        Returns the count of records that will be loaded for the inputed 
        information.
        
        :param      table_or_join | <subclass of orb.Table> || None
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     <int>
        """
        if Table.typecheck(table_or_join):
            schemas = [table_or_join.schema()]
        else:
            schemas = map(lambda x: x.schema(), table_or_join.tables())
        
        engine = self.engine()
        sql, data = engine.countCommand(schemas, lookup=lookup)
        
        results = self.execute(sql,
                               data,
                               mapper=lambda x: dict(x)['count'],
                               autoCommit=False)
        return sum(results)
    
    def commit(self):
        """
        Commits the changes to the current database connection.
        
        :return     <bool> success
        """
        if not (self.isConnected() and self.commitEnabled()):
            return False
        
        if Transaction.current():
            Transaction.current().setDirty(self)
        else:
            self.backendDb().commit()
        return True
    
    def createTable(self, schema, options):
        """
        Creates a new table in the database based cff the inputed
        schema information.  If the dryRun flag is specified, then
        the SQL will only be logged to the current logger, and not
        actually executed in the database.
        
        :param      schema    | <orb.TableSchema>
                    options   | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        if schema.isAbstract():
            name = schema.name()
            logger.debug('%s is an abstract table, not creating' % name)
            return False
        
        engine = self.engine()
        sql, data = engine.createCommand(schema)
        
        if not options.dryRun:
            self.execute(sql)
        else:
            logger.info('\n'+command+'\n')
        
        logger.info('Created %s table.' % schema.tableName())
        return True
    
    def disableInternals(self):
        """
        Disables the internal checks and update system.  This method should
        be used at your own risk, as it will ignore errors and internal checks
        like auto-incrementation.  This should be used in conjunction with
        the enableInternals method, usually these are used when doing a
        bulk import of data.
        
        :sa     enableInternals
        """
        super(SqlBase, self).disableInternals()
        
        # disable the internal processes within the database for faster
        # insertion
        engine = self.engine()
        sql = engine.command('disable_internals')
        if sql:
            self.execute(sql, autoCommit=False)
    
    def distinct(self, table_or_join, lookup, options):
        """
        Returns a distinct set of results for the given information.
        
        :param      table_or_join | <subclass of orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        if Table.typecheck(table_or_join):
            schemas = [table_or_join.schema()]
        else:
            schemas = map(lambda x:schema(), table_or_join.tables())
        
        lookup.distinct = True
        sql, data = self.engine().selectCommand(schemas, lookup=lookup)
        
        if '__RECORDS_ARE_BLANK__' in sql:
            db_results = {}
        else:
            db_results = self.execute(sql, data, autoCommit=False)
        
        output = dict([(column, set()) for column in lookup.columns])
        for schema in schemas:
            for db_result in db_results:
                for colname in lookup.columns:
                    col = schema.column(colname)
                    if not col:
                        continue
                    
                    key = '{0}_{1}'.format(col.schema().tableName(),
                                           col.fieldName())
                    output[col.name()].add(db_result.get(key))
        
        for key, value in output.items():
            output[key] = list(value)
        
        return output
    
    def enableInternals(self):
        """
        Enables the internal checks and update system.  This method should
        be used at your own risk, as it will ignore errors and internal checks
        like auto-incrementation.  This should be used in conjunction with
        the disableInternals method, usually these are used when doing a
        bulk import of data.
        
        :sa     disableInternals
        """
        # enables the internal processes within the database for protected
        # insertions and changes
        engine = self.engine()
        sql = engine.command('enable_internals')
        if sql:
            self.execute(sql, autoCommit=False)
        
        super(SqlBase, self).enableInternals()
    
    def existingColumns(self, schema, namespace=None, mapper=None):
        """
        Looks up the existing columns from the database based on the
        inputed schema and namespace information.
        
        :param      schema      | <orb.TableSchema>
                    namespace   | <str> || None
        
        :return     [<str>, ..]
        """
        if mapper is None:
            mapper = lambda x: str(x[0])
        engine = self.engine()
        sql, data = engine.columnsCommand(schema)
        return self.execute(sql, data, mapper=mapper, autoCommit=False)
    
    def execute(self, 
                command, 
                data       = None,
                autoCommit = True,
                autoClose  = True,
                returning  = True,
                mapper     = dict,
                retries    = 3):
        """
        Executes the inputed command into the current \
        connection cursor.
        
        :param      command    | <str>
                    data       | <dict> || None
                    autoCommit | <bool> | commit database changes immediately
                    autoClose  | <bool> | closes connections immediately
                    returning  | <bool>
                    mapper     | <variant>
                    retries    | <int>
        
        :return     [{<str> key: <variant>, ..}, ..]
        """
        if data is None:
            data = {}
        
        if not self.open():
            raise errors.ConnectionError('Failed to open connection.',
                                         self.database())
        
        # when in debug mode, simply log the command to the logger
        elif self.database().commandsBlocked():
            logger.info(command % data)
            return []
        
        results = []
        for i in range(retries):
            try:
                results = self._execute(command,
                                        data,
                                        autoCommit,
                                        autoClose,
                                        returning,
                                        mapper)
                break
            
            # always raise interruption errors as these need to be handled
            # from a thread properly
            except errors.Interruption:
                raise
            
            # attempt to reconnect as long as we have enough retries left
            # otherwise raise the error
            except errors.ConnectionLostError, err:
                if i != (retries - 1):
                    time.sleep(0.25)
                    self.reconnect()
                else:
                    raise
            
            # handle any known a database errors with feedback information
            except errors.DatabaseError, err:
                if self.isConnected():
                    if Transaction.current():
                        Transaction.current().rollback(err)
                    
                    try:
                        self.rollback()
                    except:
                        pass
                    
                    raise
                else:
                    raise
            
            # always raise any unknown issues for the developer
            except StandardError:
                raise
        
        return results
        
    def insert(self, records, lookup, options):
        """
        Inserts the table instance into the database.  If the
        dryRun flag is specified, then the command will be 
        logged but not executed.
        
        :param      records  | <orb.Table>
                    lookup   | <orb.LookupOptions>
                    options  | <orb.DatabaseOptions>
        
        :return     <dict> changes
        """
        # convert the recordset to a list
        if RecordSet.typecheck(records):
            records = list(records)
        
        # wrap the record in a list
        elif Table.recordcheck(records):
            records = [records]
        
        # determine the proper records for insertion
        inserter = {}
        changes = []
        for record in records:
            # make sure we have some data to insert
            rchanges = record.changeset(columns=lookup.columns)
            changes.append(rchanges)
            
            # do not insert records that alread exist
            if record.isRecord():
                continue
            
            elif not rchanges:
                continue
            
            schema = record.schema()
            inserter.setdefault(schema, [])
            inserter[schema].append(record)
        
        cmds = []
        data = {}
        setup = {}
        
        engine = self.engine()
        for schema, schema_records in inserter.items():
            if not schema_records:
                continue
            
            for batch in projex.iters.batch(schema_records,
                                            self.insertBatchSize()):
                batch = list(batch)
                icmd, idata = engine.insertCommand(schema,
                                                   batch,
                                                   columns=lookup.columns,
                                                   setup=setup)
                cmds.append(icmd)
                data.update(idata)
            
            # for inherited schemas in non-OO tables, we'll define the
            # primary keys before insertion
            if not schema.inherits() or self.isObjectOriented():
                cmd, dat = engine.insertedCommand(schema, count=len(batch))
                cmds.append(cmd)
                data.update(dat)
        
        if not cmds:
            return {}
        
        sql = '\n'.join(cmds)
        results = self.execute(sql, data, autoCommit=False)
        
        if not self.commit():
            if len(changes) == 1:
                return {}
            return []
        
        # update the values for the database
        for i, record in enumerate(records):
            try:
                record._updateFromDatabase(results[i])
            except IndexError:
                pass
            
            record._markAsLoaded(self.database(), columns=lookup.columns)
        
        if len(changes) == 1:
            return changes[0]
        return changes
    
    def insertBatchSize(self):
        """
        Returns the maximum number of records that can be inserted for a single
        insert statement.
        
        :return     <int>
        """
        return self._insertBatchSize
    
    def interrupt(self, threadId=None):
        """
        Interrupts the access to the database for the given thread.
        
        :param      threadId | <int> || None
        """
        cid = threading.current_thread().ident
        if threadId is None:
            cid = threading.current_thread().ident
            for tid, thread_db in self._thread_dbs.items():
                if tid != cid:
                    thread_db.interrupt()
                    self._thread_dbs.pop(tid)
        else:
            thread_db = self._thread_dbs.get(threadId)
            if not thread_db:
                return
            
            if threadId == cid:
                thread_db.close()
            else:
                self._interrupt(threadId, thread_db)
            
            self._thread_dbs.pop(threadId)
    
    def isConnected(self):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return self.backendDb() != None
    
    def isObjectOriented(self):
        """
        Returns whether or not this database supports object-oriented tables
        by default.
        
        :return     <bool>
        """
        return self._objectOriented
    
    def open(self):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        tid = threading.current_thread().ident
        
        # clear out old ids
        for thread in threading.enumerate():
            if not thread.isAlive():
                self._thread_dbs.pop(thread.ident, None)
        
        thread_db = self._thread_dbs.get(tid)
        
        # check to see if we already have a connection going
        if thread_db:
            return True
        
        # make sure we have a database assigned to this backend
        elif not self._database:
            raise errors.DatabaseNotFoundError()
        
        # open a new backend connection to the database for this thread
        backend_db = self._open(self._database)
        if backend_db:
            self._thread_dbs[tid] = backend_db
            Orb.instance().runCallback(CallbackType.ConnectionCreated,
                                       self._database)
        else:
            Orb.instance().runCallback(CallbackType.ConnectionFailed,
                                       self._database)
        
        return backend_db != None
    
    def reconnect(self):
        """
        Forces a reconnection to the database.
        """
        tid = threading.current_thread().ident
        db = self._thread_dbs.pop(tid, None)
        if db:
            try:
                db.close()
            except:
                pass
        
        return self.open()
    
    def removeRecords(self, remove, options):
        """
        Removes the inputed record from the database.
        
        :param      remove  | {<orb.TableSchema>: [<variant> key, ..], ..}
                    options | <orb.DatabaseOptions>
        
        :return     <int> number of rows removed
        """
        if not remove:
            return 0
        
        cmds = []
        data = {}
        
        # include various schema records to remove
        engine = self.engine()
        for schema, records in remove.items():
            if not records:
                continue
            
            icmd, idata = engine.removeCommand(schema, records)
            cmds.append(icmd)
            data.update(idata)
        
        if not cmds:
            return 0
        
        sql = '\n'.join(cmds)
        results = self.execute(sql, data)
        
        return sum(map(len, remove.values()))
    
    def rollback(self):
        """
        Rolls back changes to this database.
        """
        db = self.backendDb()
        if db:
            db.rollback()
            return True
        return False
    
    def select(self, table_or_join, lookup, options):
        """
        Selects from the database for the inputed items where the
        results match the given dataset information.
        
        :param      table_or_join   | <subclass of orb.Table> || <orb.Join>
                    lookup          | <orb.LookupOptions>
                    options         | <orb.DatabaseOptions>
        
        :return     [({<str> columnName: <variant> value, .., ..), ..]
        """
        if Table.typecheck(table_or_join):
            schemas = [table_or_join.schema()]
        else:
            schemas = [table.schema() for table in table_or_join.tables()]
        
        datamapper = {}
        engine = self.engine()
        sql, data = engine.selectCommand(schemas,
                                         lookup=lookup,
                                         datamapper=datamapper)
        
        if '__RECORDS_ARE_BLANK__' in sql:
            db_records = []
        else:
            db_records = self.execute(sql, data, autoCommit=False)
        
        # restore the records from the database
        output = []
        is_oo = self.isObjectOriented()
        db = self.database()
        for db_record in db_records:
            records = {}
            for db_key in db_record:
                column = datamapper.get(db_key)
                if not column:
                    continue
                
                engine = column.engine(db)
                value  = engine.unwrap(column, db_record[db_key])
                
                schema = column.firstMemberSchema(schemas)
                records.setdefault(schema, {})
                records[schema][column.name()] = value
            
            out_records = []
            for schema in schemas:
                out_records.append(records.get(schema))
            output.append(out_records)
        
        if Table.typecheck(table_or_join):
            return map(lambda x: x[0], output)
        return output
    
    def setInsertBatchSize(self, size):
        """
        Sets the maximum number of records that can be inserted for a single
        insert statement.
        
        :param      size | <int>
        """
        self._insertBatchSize = size
    
    def setObjectOriented(self, state):
        """
        Sets whether or not this database supports object-oriented tables
        by default.
        
        :param      state | <bool>
        """
        self._objectOriented = state
    
    def setRecords(self, schema, records, **options):
        """
        Restores the data for the inputed schema.
        
        :param      schema  | <orb.TableSchema>
                    records | [<dict> record, ..]
        """
        if not records:
            return
        
        engine = self.engine()
        cmds = []
        data = {}
        
        # truncate the table
        cmd, dat = engine.truncateCommand(schema)
        self.execute(cmd, dat, autoCommit=False)
        
        # disable the tables keys
        cmd, dat = engine.disableInternalsCommand(schema)
        self.execute(cmd, dat, autoCommit=False)
        
        # insert the records
        cmds  = []
        dat   = {}
        setup = {}
        for batch in projex.iters.batch(records, self.insertBatchSize()):
            batch = list(batch)
            icmd, idata = engine.insertCommand(schema,
                                               batch,
                                               columns=options.get('columns'),
                                               autoincrement=False,
                                               setup=setup)
            cmds.append(icmd)
            dat.update(idata)
        
        self.execute('\n'.join(cmds), dat, autoCommit=False)
        
        # enable the table keys
        cmd, dat = engine.enableInternalsCommand(schema)
        self.execute(cmd, dat)
    
    def tableExists(self, schema, options):
        """
        Checks to see if the inputed table class exists in the
        database or not.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <bool> exists
        """
        engine = self.engine()
        sql, data = engine.existsCommand(schema)
        if not sql:
            return False
        
        results = self.execute(sql, data, autoCommit=False)
        if results:
            return True
        return False
    
    def update(self, records, lookup, options):
        """
        Updates the modified data in the database for the 
        inputed record.  If the dryRun flag is specified then
        the command will be logged but not executed.
        
        :param      record   | <orb.Table>
                    lookup   | <orb.LookupOptions>
                    options  | <orb.DatabaseOptions>
        
        :return     <dict> changes
        """
        # convert the recordset to a list
        if RecordSet.typecheck(records):
            records = list(records)
        
        # wrap the record in a list
        elif Table.recordcheck(records):
            records = [records]
        
        is_oo = self.isObjectOriented()
        updater = {}
        changes = []
        for record in records:
            rchanges = record.changeset(columns=lookup.columns)
            changes.append(rchanges)
            
            if not record.isRecord():
                continue
            
            elif not rchanges:
                continue
            
            if not is_oo:
                schemas = record.schema().ancestry() + [record.schema()]
            else:
                schemas = [record.schema()]
            
            for schema in schemas:
                updater.setdefault(schema, [])
                updater[schema].append(record)
        
        if not updater:
            if len(records) > 1:
                return []
            else:
                return {}
        
        cmds = []
        data = {}
        
        engine = self.engine()
        for schema, schema_records in updater.items():
            icmd, idata = engine.updateCommand(schema,
                                               schema_records,
                                               columns=lookup.columns)
            cmds.append(icmd)
            data.update(idata)
        
        sql = '\n'.join(cmds)
        results = self.execute(sql, data, autoCommit=False)
        
        if not self.commit():
            if len(changes) == 1:
                return {}
            return []
        
        # update the values for the database
        for record in records:
            record._markAsLoaded(self.database(), columns=lookup.columns)
        
        if len(changes) == 1:
            return changes[0]
        return changes
    
    def updateTable(self, schema, options):
        """
        Determines the difference between the inputed schema
        and the table in the database, creating new columns
        for the columns that exist in the schema and do not
        exist in the database.  If the dryRun flag is specified,
        then the SQL won't actually be executed, just logged.

        :note       This method will NOT remove any columns, if a column
                    is removed from the schema, it will simply no longer 
                    be considered part of the table when working with it.
                    If the column was required by the db, then it will need to 
                    be manually removed by a database manager.  We do not
                    wish to allow removing of columns to be a simple API
                    call that can accidentally be run without someone knowing
                    what they are doing and why.
        
        :param      schema     | <orb.TableSchema>
                    options    | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        # determine the new columns
        existing = self.existingColumns(schema)
        missing  = schema.columns(recurse=False,
                                  includeProxies=False,
                                  includeJoined=False,
                                  includeAggregates=False,
                                  ignore=existing)
        
        # if no columns are missing, return True to indicate the table is
        # up to date
        if not missing:
            return True
        
        engine = self.engine()
        sql, data = engine.alterCommand(schema, missing)
        if options.dryRun:
            logger.info('\n'+sql+'\n')
        else:
            self.execute(sql, data)
            
            opts = (schema.name(),
                    ','.join(map(lambda x: x.fieldName(), missing)))
            logger.info('Updated {0} table: added {1}'.format(*opts))
        
        return True
