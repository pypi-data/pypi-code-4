#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

from pyar.dialects.connection import Database, ConnectPool
from pyar import exc
import MySQLdb

try:
	from DBUtils.PooledDB import PooledDB
except ImportError as e:
    print e
    raise e

class Sqlite(Database):
	_url         = None
	_using       = 'default'
	_pool        = None
	logger       = None

	def __init__(self, using, url):
		"""url is dns url"""
		self._using = using
		self._url   = url
		
		self._pool = None

	def getconn(self):
		'''It should return a connection.'''
		return self._pool.connection()

	def getcur(self, conn):
		return conn.cursor(MySQLdb.cursors.DictCursor)

	def putconn(self, conn):
		conn.close()

	def prepare(self, sql):
		return sql.replace('%s', '?')

dialect = Sqlite
