from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import or_
import os

class SQLite3Vocab(object):

    singleton = False
    def __init__(self):
        if not self.singleton:
            self.__class__.singleton = True
        else:
            raise SystemError, 'SQLite3Vocab is singleton.'
        path = os.path.dirname( os.path.realpath( __file__ ) )
        self.engine = SqlSoup('sqlite:////%s/sqlite3.db' % path)
        self.comune_id = self.engine.comuni.codice_istat
        self.provincia_id = self.engine.province.sigla
        self.regione_id = self.engine.regioni.codice_istat

    def _filter_ente(self, tabel, sql_filters=None):
        if sql_filters:
            for sql_filter in sql_filters:
                tabel = tabel.filter(sql_filter)
        return tabel

    def comune(self, name):
        return self.engine.comuni.filter_by(comune=name).one()

    def provincia(self, name):
        return self.engine.province.filter_by(provincia=name).one()

    def regione(self, name):
        return self.engine.regioni.filter_by(regione=name).one()

    def comuni(self, sql_filters=None):
        query = self._filter_ente(self.engine.comuni, sql_filters)
        return query.order_by(self.engine.comuni.comune).all()

    def province(self, sql_filters=None):
        query = self._filter_ente(self.engine.province, sql_filters)
        return query.order_by(self.engine.province.provincia).all()

    def regioni(self, sql_filters=None):
        query = self._filter_ente(self.engine.regioni, sql_filters)
        return query.order_by(self.engine.regioni.regione).all()

    def comuniByLetter(self, query):
        where = (or_(self.engine.comuni.comune.like(query+'%')),)
        return self.comuni(sql_filters=where)

    def provinceByLetter(self, query):
        where = (or_(self.engine.province.provincia.like(query+'%')),)
        return self.province(sql_filters=where)

    def regioniByLetter(self, query):
        where = (or_(self.engine.regioni.regione.like(query+'%')),)
        return self.regioni(sql_filters=where)

    def comuni4provincia(self, id):
        where = or_(self.engine.comuni.provincia==id)
        return self.engine.comuni.filter(where).order_by(self.engine.comuni.comune).all()

    def province4regione(self, id):
        where = or_(self.engine.province.regione==id)
        return self.engine.province.filter(where).order_by(self.engine.province.provincia).all()

    #Backward compatibility
    allComuni = comuni
    allProvince = province
    allRegioni = regioni

def mapDisplayList(vocab, result=None):
    if not result:
        result = []
    for x in vocab:
        if x._table.name == 'regioni':
            row = (x.codice_istat, x.regione)
        elif x._table.name == 'province':
            row = (x.sigla, x.provincia)
        elif x._table.name == 'comuni':
            row = (x.codice_istat, x.comune)
        result.append(row)
    return result
