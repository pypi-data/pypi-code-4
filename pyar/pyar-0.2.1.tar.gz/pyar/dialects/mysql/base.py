#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

from pyar.dialects.connection import Database, ConnectPool
from pyar import exc, util
import MySQLdb

try:
	'''
    dbapi: 需要使用的DB-API 2模块
    mincached : 启动时开启的空连接数量(缺省值 0 意味着开始时不创建连接)
    maxcached: 连接池使用的最多连接数量(缺省值 0 代表不限制连接池大小)
    maxshared: 最大允许的共享连接数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量，被请求为共享的连接将会被共享使用。
    maxconnections: 最大允许连接数量(缺省值 0 代表不限制)
    blocking: 设置在达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误；其他代表阻塞直到连接数减少)
    maxusage: 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用)。当达到最大数值时，连接会自动重新连接(关闭和重新打开)
    setsession: 一个可选的SQL命令列表用于准备每个会话，如 ["set datestyle to german", ...]
    其他，你可以设置用于传递到真正的DB-API 2的参数，例如主机名、数据库、用户名、密码等。
    PooledDB.PooledDB(creator=MySQLdb, 
		mincached=10,
		maxcached=10,
		host=DBConfig.host,
		port=DBConfig.port,
		user=DBConfig.username,
		passwd=DBConfig.password,
		db=DBConfig.database_name,
		use_unicode=DBConfig.use_unicode,
		charset=DBConfig.charset)
	'''
	from DBUtils.PooledDB import PooledDB
except ImportError as e:
    raise e

class MySQL(Database):
    _url         = None
    _using       = 'default'
    _pool        = None

    def __init__(self, using, url):
        """url is dns url"""
        self._using = using
        self._url   = url

        _use_unicode    = False
        _mincached      = 20
        _maxcached      = 100
        _maxshared      = 0
        _maxconnections = 0
        _blocking       = 1
        _maxusage       = 0
        _setsession     = ''
        try:
            _mincached = self._url.query.get('mincached', _mincached)
            _mincached = int(_mincached)
        except:
            pass
        try:
            _maxcached = self._url.query.get('maxcached', _maxcached)
            _maxcached = int(_maxcached)
        except:
            pass
        try:
            _maxshared = self._url.query.get('maxshared', _maxshared)
            _maxshared = int(_maxshared)
        except:
            pass
        try:
            _maxconnections = self._url.query.get('maxconnections', _maxconnections)
            _maxconnections = int(_maxconnections)
        except:
            pass
        try:
            _blocking = self._url.query.get('blocking', _blocking)
            _blocking = int(_blocking)
        except:
            pass
        try:
            _maxusage = self._url.query.get('maxusage', _maxusage)
            _maxusage = int(_maxusage)
        except:
            pass
        try:
            _setsession = self._url.query.get('setsession', _setsession)
            _setsession = str(_setsession).strip()
        except:
            pass
        try:
            _use_unicode = self._url.query.get('use_unicode', _use_unicode)
            _use_unicode = bool(int(_use_unicode))
        except:
            pass
        _pool = ConnectPool.getPool(using)
        if _pool is None:
            try:
                _params = dict(creator=MySQLdb,
                               mincached=_mincached,
                               maxcached=_maxcached,
                               maxshared=_maxshared,
                               maxconnections=_maxconnections,
                               blocking=_blocking,
                               maxusage=_maxusage,
                               host=self._url.host or 'localhost',
                               port=self._url.port or 3306,
                               user=self._url.username,
                               passwd=self._url.password,
                               db=self._url.database,
                               use_unicode=_use_unicode,
                               charset=self._url.query.get('charset', 'utf8'),)
                if _setsession:
                    _params.update(dict(setsession=_setsession))
                _pool = PooledDB(**_params)
                self._pool = _pool
                ConnectPool.putPool(using, _pool)
            except Exception as e:
                raise exc.DBConnectionError("Database Connection Error '%s' for '%s'" % (e, using))
        else:
            self._pool = _pool

    def getconn(self):
        '''It should return a connection.'''
        return self._pool.connection()

    def getcur(self, conn):
        return conn.cursor(MySQLdb.cursors.DictCursor)

    def putconn(self, conn):
        conn.close()

    def prepare(self, sql):
        return sql

    def dumpSQL(self, sql, params, using):
        tpl = '''
        --- SQL DUMP ---
        using: {0}
        {1} - {2}
        raw_sql: {3};
        --- END DUMP ---
        '''
        rparams = []
        for p in params:
            if isinstance(p, str) or isinstance(p, unicode):
                rparams.append("'%s'" % MySQLdb.escape_string(p))
            else:
                rparams.append(p)
        #print tpl.format(using, sql, params)
        util.logger.debug(tpl.format(using, sql, params, sql % tuple(rparams)))

dialect = MySQL
