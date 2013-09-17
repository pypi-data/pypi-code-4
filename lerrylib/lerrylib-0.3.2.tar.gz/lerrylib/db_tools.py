#!/usr/bin/python
# -*- coding: utf-8 -*-
import _mysql
from torndb import Row
from cache import mc as _mc
from lerry_signal import SIGNAL
from torndb import Connection as _Connection
from msgpack import packb, unpackb


class Model(object):

	def KEY(self, id):
		return '%s:%s' % (self._table, id)

	def __init__(self, name, db):
		self._table = name
		self.db = db
		self.mc = db.mc

	def get(self, id):
		id = int(id)
		MC_KEY = self.KEY(id)
		item = self.mc.get(MC_KEY)
		if item is None:
			item = self.db.get('select * from %s where id = %%s' % self._table, id)
			self.mc.set(MC_KEY, packb(item))
		else:
			item = Row(unpackb(item))
		return item

	def get_list(self, id_list):
		_di = self.mc.get_multi(map(self.KEY, id_list))

		result = []
		for id in id_list:
			value = _di.get(id)
			if value is None:
				value = self.get(id)
			result.append(value)
		return map(Row, result)

	def rm(self, id):
		self.db.query('delete from %s where id = %%s' % self._table, id)
		self.mc.delete('%s:%s' % (self._table, id))

def _getattr(self, name):
	self.query('select 1 from %s' % name)
	return Model(name, self)

def _execute(self, cursor, query, parameters):
    try:
        result = cursor.execute(query, parameters)
        SIGNAL.db_query.send(cursor._last_executed)
        return result
    except OperationalError:
        logging.error("Error connecting to MySQL on %s", self.host)
        self.close()
        raise

def Connection(host, db, user, pw, mc=None):
	'''
		wrapper of torndb
	'''
	if mc is None:
		mc = _mc
	_Connection.__getattr__ = _getattr
	_Connection.mc = mc
	_Connection._execute = _execute
	return _Connection(host, db, user, pw)
		



		
if __name__ == '__main__':
	pass
