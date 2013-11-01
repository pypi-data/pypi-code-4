"""
this is a really tiny orm-ish layer, just for sake of simplicity
other than that building up insert/update queries it doesnt do much,
its not a real orm
"""
import os
import sqlite3
from contextlib import contextmanager

class Column(object):
    def __init__(self, coltype, **kwargs):
        self.coltype = coltype
        self.index = False
        if 'index' in kwargs:
            self.index = True
            del kwargs['index']
        self.extargs = kwargs

    def get_ext_args(self):
        s = ""
        for i in self.extargs:
            if i == 'primary':
                s += 'primary key '
            else:
                s += "%s %s " % (i, self.extargs[i])
        return s

class DBObject(object):

    columns = {}

    def __init__(self, **kwargs):
        object.__setattr__(self, 'data', {})

        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key in self.__class__.columns:
            self.__dict__['data'][key] = value
        else:
            self.__dict__[key] = value

class OpContext(object):
    def __init__(self, connection):
        self.objects = []
        self.connection = connection

    def add(self, obj):
        self.objects.append(obj)

    def get_insert_query(self, obj):
        query = "insert into %s(" % obj.__class__.__tablename__
        query += ','.join(obj.data.keys())
        query += ') values ( '
        query += ', '.join(['?'] * len(obj.data.keys()))
        query += ');'
        return (query, obj.data.values())

    def get_update_query(self, obj):
        query = "update %s " % obj.__class__.__tablename__
        query += " set "
        w = []
        for k in obj.data:
            w += ["%s=?" % k]
        query += ','.join(w)
        query += " where id=?"
        #print query
        return (query, obj.data.values() + [obj.data['id']])

    def save(self):
        queries = []
        for obj in self.objects:
            if 'id' in obj.data and obj.data['id']:
                queries.append(self.get_update_query(obj))
            else:
                queries.append(self.get_insert_query(obj))
        cursor = self.connection.cursor()
        for q, values in queries:
            cursor.execute(q, values)

class Database(object):
    def __init__(self, path, init_if_not_exists=True, models=None):
        self.models = set()
        if models:
            for model in models:
                self.add_model(model)
        do_init = False
        if not os.path.exists(path):
            do_init = init_if_not_exists
        self.con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.con.row_factory = sqlite3.Row
        if do_init:
            self.init_database()

    def _build_where_clause_from_kw(self, klass, **kwargs):
        query = ""
        w = []
        for k in kwargs:
            w += ["%s = ?" % k]
        query += ' and '.join(w)
        return (query, kwargs.values())

    def _build_get_query(self, klass, **kwargs):
        order_by = None
        if 'order_by' in kwargs:
            order_by = kwargs['order_by']
            del kwargs['order_by']

        query = """
        select * from %s
        """ % klass.__tablename__

        where_clause, where_values = self._build_where_clause_from_kw(klass, **kwargs)

        query += "where %s " % where_clause

        if order_by:
            query += ' order by %s' % order_by

        return (query, kwargs.values())

    def remove(self, klass, **kwargs):
        query = " delete from %s " % klass.__tablename__
        where_clause, where_values = self._build_where_clause_from_kw(klass, **kwargs)
        query += "where %s " % where_clause
        cur = self.con.cursor()
        cur.execute(query, where_values)
        self.con.commit()

    def get_all(self, klass, **kwargs):
        query, values = self._build_get_query(klass, **kwargs)
        cur = self.con.cursor()
        cur.execute(query, values)
        rows = cur.fetchall()
        return map(lambda row: klass(**row), rows)

    def get(self, klass, **kwargs):
        query, values = self._build_get_query(klass, **kwargs)
        cur = self.con.cursor()
        cur.execute(query, values)
        row = cur.fetchone()
        if row:
            return klass(**row)

    @contextmanager
    def context(self):
        ops = OpContext(self.con)
        yield ops
        self.con.commit()

    def add_model(self, model):
        if not 'id' in model.columns:
            model.columns['id'] = Column('integer', primary='key')
        self.models.add(model)

    def init_database(self):
        cursor = self.con.cursor()

        for model in self.models:
            query = "create table %s (" % model.__tablename__
            columns = []
            for colname, column in model.columns.iteritems():
                columns += ["%s %s %s" % (colname,
                                          column.coltype,
                                          column.get_ext_args()) ]
            query += ','.join(columns) + ");"
            #print query
            cursor.execute(query)

            for colname, column in model.columns.iteritems():
                if column.index:
                    query = 'create index ndx_%s_%s on %s(%s)' % (model.__tablename__, colname,
                                                                  model.__tablename__, colname)
                    cursor.execute(query)
        self.con.commit()