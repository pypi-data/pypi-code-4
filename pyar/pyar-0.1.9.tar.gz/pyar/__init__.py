#-*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

__author__  = 'Jefurry <jefurry@qq.com>'
__version__ = '0.1.9'

import traceback
from sqlbuilder import smartsql as sb
from pyar import exc, url, util, result
from pyar.dialects import connection
import pyar.settings

T, TA, F, A, E, qs = sb.Table, sb.TableAlias, sb.Field, sb.Alias, sb.Expr, sb.QuerySet
const = sb.ConstantSpace()
func = sb.const
qn = sb.Name()

DEFAULT_DIALECT = 'mysql'
sb.default_dialect(DEFAULT_DIALECT)

SMARTSQL_DIALECTS = {
    'sqlite3': 'sqlite',
    'sqlite' : 'sqlite',
    'mysql': 'mysql',
    'postgresql': 'postgres',
    'postgresql_psycopg2': 'postgres',
    'postgis': 'postgres',
    'oracle': 'oracle',
}

logger = util.getLogger('pyar')
def dumpSQL(sql, params, using='default'):
    tpl = '''
    --- SQL DUMP ---
    using: {0}
    {1} - {2}
    --- END DUMP ---
    '''
    print tpl.format(using, sql, params)
    #logger.debug(tpl, using, sql, params)

NoneResult    = result.Result(None)
NoneRowResult = result.RowResult(None)

class ModelBase(object):
    _auto_commit_  = True
    _using_        = 'default'
    _debug_        = False
    _primary_key_  = 'id'
    _db_name_      = None
    _tb_name_      = None

class Model(ModelBase):
    db      = None
    qs      = None
    _conn   = None
    _db_key = None
    _tb_key = None
    #T, TA, F, A, E, qs = sb.Table, sb.TableAlias, sb.Field, sb.Alias, sb.Expr, sb.QuerySet
    #const = sb.ConstantSpace()
    #func = sb.const
    #qn = sb.Name()

    def __init__(self):
    	_using      = None
    	if not hasattr(self, '_using_'):
    		pass
    	else:
    		_using = self._using_
    	if _using is None:
    		_using = 'default'
        self._using = _using

    	_dns = pyar.settings.DNS.get(_using, None)
        if not _dns:
        	raise exc.DnsStringNotFoundError(
        		"Not Found DNS String '%s' for settings" % _using)
        else:
            _dns_url = url.make_url(_dns)
            _dialect = _dns_url.get_dialect()
            if issubclass(_dialect, connection.Database):
                self.db    = _dialect(_using, _dns_url)
                self._conn = self.db.getconn()
                _tbname    = None
                if hasattr(self, '_tb_name_'):
                    if callable(self._tb_name_) and hasattr(self, '_tb_key'):
                        _tbname = self._tb_name_(self._tb_key)
                    else:
                        _tbname = self._tb_name_
                if _tbname:
                    self.qs = sb.QuerySet(getattr(sb.Table, _tbname))
                    self.qs._dialect = _dns_url.drivername
                else:
                    raise exc.DBTableNotExistsError("Table Not Exists.")
            else:
                raise exc.DialectNotFoundError("Not Found Dialect for '%s'" % _using)

    def autocommit(self, val=None):
        if val is None:
            return self._auto_commit_
        else:
            self._auto_commit_ = val
            return val

    def use(self, db_key=None, tb_key=None):
        self._db_key = db_key
        self._tb_key = tb_key
        if self._tb_key is None:
            self._tb_key = self._db_key
        return self

    def begin(self):
        pass

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def _execute(self, sql, params, action=None):
        if self._debug_:
            dumpSQL(sql, params, self._using)
        _cur    = self.db.getcur(self._conn)
        _dbname = None
        if hasattr(self, '_db_name_'):
            if callable(self._db_name_) and hasattr(self, '_db_key'):
                _dbname = self._db_name_(self._db_key)
            else:
                _dbname = self._db_name_
        if _dbname:
            _cur.execute('USE `%s`' % (_dbname,))

        _res    = _cur.execute(self.db.prepare(sql), params)
        _lastid = None
        if action == 'insert':
            _lastid = _cur.lastrowid
        elif action == 'select_all':
            _res = _cur.fetchall()
        elif action == 'select_one':
            _res = _cur.fetchone()
        elif action == 'select_count':
            _res = _cur.fetchone()
        else:
            pass

        _cur.close()
        if self.autocommit():
            self.commit()
            #self.end()
        if _lastid is not None:
            return _lastid

        return _res

    def insert(self, sql):
        try:
            return self._execute(sql[0], sql[1], 'insert')
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def _select(self, sql, flag='select_all'):
        try:
            return self._execute(sql[0], sql[1], flag)
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def all(self, sql):
        try:
            _res = self._select(sql, 'select_all')
            if not _res or len(_res) <= 0:
                _res = None
            return result.Result.new(_res)
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def first(self, sql):
        try:
            _res = self._select(sql, 'select_one')
            if not _res or len(_res) <= 0:
                _res = None
            return result.RowResult.new(_res)
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))


    def count(self, sql):
        try:
            _res = self._select(sql, 'select_count')
            if not _res or len(_res) <= 0:
                return 0
            for key in _res:
                return _res[key]
            return 0
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def update(self, sql):
        u'''返回受影响行数'''
        try:
            return self._execute(sql[0], sql[1], 'update')
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def delete(self, sql):
        u'''返回受影响行数'''
        try:
            return self._execute(sql[0], sql[1], 'delete')
        except Exception as e:
            if self._debug_:
                logger.debug(e)
            raise exc.DBOperationError("Database Operation Error: '%s'." % (e,))

    def end(self):
        try:
            self.db.putconn(self._conn)
            self._conn = None
        except:
            pass

    def __del__(self):
        self.end()

    def __enter__(self):
        return self

    def __exit__(self, type, value, _traceback):
        _debug = self._debug_
        del self
        if _traceback is not None:
            if _debug:
                print "with exit error: ", traceback.format_exc()
            return False
        return True


if __name__ == '__main__':
    import time, sys

    pyar.settings.DNS = {
    'default' : 'mysql://root:@localhost:3306/davos?use_unicode=0&charset=utf8&mincached=20&maxcached=100',
    }

    class DavosDatabase(Model):
        _debug_ = True
        _using_ = 'default'

    class AppModel(DavosDatabase):
        _tb_name_ = 'app'
        _db_name_ = lambda cls, key: 'davos'

    a = AppModel()
    _time = int(time.time())
    s = a.qs.insert({'user_id' : 1, 
        'title' : 'good,night', 
        'name' : 'test', 
        'description' : "'ttt'", 
        'ctime' : _time, 
        'mtime' : _time, 
        'enable' : 1})

    #print s
    a.insert(s)
    #print a.qs.where(sb.F.id==2).select('*')
    print '---------------------------------------'
    a.count(a.qs.count('*'))
    print '---------------------------------------'
    #print a.qs.where(sb.F.id==2).update({'title' : 'goal'})
    a.update(a.qs.where(sb.F.id>2).update({'title' : 'goal'}))
    print '---------------------------------------'
    #print a.qs.where(sb.F.id==2).delete()
    a.delete(a.qs.where(sb.F.id>260).delete())
    print '---------------------------------------'
    res = a.all(a.qs.where(sb.F.id==1).select('*'))
    print res.id, res.name
    for row in res:
        print row.name, row.id, '@===@'
    print "raw: ", res.raw()
    res2 = a.all(a.qs.where(sb.F.id==2).select('*'))
    print "+++++++++++++++++++++++++++++++++++++++++++++++"
    print ".....", (res + res2).raw(), "...."
    print "+++++++++++++++++++++++++++++++++++++++++++++++"
    print '---------------------------------------'
    res3 = a.first(a.qs.select('*'))
    print res3.id, res3.name
    for k, v in res3:
        print k, v, '*===*'
    print "raw: ", res3.raw()
    print "????", (res + res).raw(), "????"
    print "$$$$", result.Result.fromRowResult(res3).raw(), "$$$$"
    print '---------------------------------------'
    print "###", res | None, result.RowResult.new() | res, "###"
    print '---------------------------------------'
    print "isinstance: ", isinstance(res, result.ResultProxy), "issubclass: ", issubclass(res.__class__, result.ResultProxy)
    print "new: ", res3.raw(), '---', res.raw(), '---', (res3 + res).raw(), '---', (res3 + {'a':'b'}).raw()
    print "+++: ", (res3 + res3).raw()
    print "************************************************************************"
    print '--------', (((res + {'gg':'goal'}) + res3) + res).raw(), '---------------'
    print type((res + {'gg':'goal'}) + res3)
    del a
    #print sb.QS(getattr(sb.T, 'user_98')).where((sb.F.status == 1) & (sb.F.a == 'go')).delete()
    #print u.tables(sb.T.good).select('*')
