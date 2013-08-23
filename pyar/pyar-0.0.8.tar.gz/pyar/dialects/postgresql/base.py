#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

from pyar.dialects.connection import Database, ConnectPool
from pyar import exc

class PostgreSQL(Database):
	pass

dialect = PostgreSQL
