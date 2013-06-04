# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import os.path
import sqlite3
from datetime import datetime as d
import random
import math

import MySQLdb as mysql

from . import TestCase, mysqlConfig
from ns import NestedSetsTree
from compat.mysqldb import Mysqldb as MysqlWrapper
from compat.sqlite3 import Sqlite3 as SqliteWrapper


repeat = 16

def stddev(vector):
  n    = 0
  mean = 0.0
  M2   = 0.0

  for x in vector:
    n    += 1
    delta = x - mean
    mean  = mean + delta / n
    M2    = M2 + delta * (x - mean)

  return math.sqrt(M2 / (n - 1))


class TestNsBigMysql(TestCase):
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    
    super(TestNsBigMysql, self).setUp()
    self.testee = NestedSetsTree(self.db, 'big', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
  
  def testMethodCoverage(self):
    pass
  
  def _getIds(self):
    cursor = self.db.cursor()
    cursor.execute('SELECT node_id FROM big')
    return tuple(r[0] for r in cursor)    
  
  def _printResults(self, times):
    times = times[1:-1]
    stats = (sum(times) / len(times), min(times), max(times), stddev(times))
    print '| mean   | min    | max    | stddev |'
    print '|',
    for v in stats:
      print '{0:.4f} |'.format(v),
    print 
  
  def testMove(self):
    ids   = self._getIds()
    times = []
    for _ in range(repeat):
      s = d.now()
      self.testee.move(random.choice(ids), parentId = random.choice(ids))
      times.append((d.now() - s).total_seconds())
      
    self._printResults(times)
  
  def testGetPath(self):
    ids   = self._getIds()
    times = []
    for _ in range(repeat):
      s = d.now()
      self.testee.getPath(random.choice(ids))
      times.append((d.now() - s).total_seconds())
      
    self._printResults(times)
    
  def testGetDescendants(self):
    ids   = self._getIds()
    times = []
    for _ in range(repeat):
      s = d.now()
      self.testee.getDescendants(random.choice(ids))
      times.append((d.now() - s).total_seconds())
      
    self._printResults(times)    

  def testValidate(self):
    times = []
    for _ in range(repeat):
      s = d.now()
      self.testee.validate(True)
      times.append((d.now() - s).total_seconds())
      
    self._printResults(times)


class TestNsBigMysqlMemorized(TestNsBigMysql):
  
  def setUp(self):
    super(TestNsBigMysqlMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db 
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
  
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsBigMysqlMemorized, self).tearDown()


class TestNsBigSqlite(TestNsBigMysql):
  
  def setUp(self):
    self.db = SqliteWrapper(sqlite3.connect(os.path.dirname(__file__) + '/fixture/sqlite.db'))
    
    TestCase.setUp(self)
    
    self.testee = NestedSetsTree(self.db, 'big', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
  
  def testMethodCoverage(self):
    pass


class TestNsBigSqliteMemorized(TestNsBigSqlite):
  
  def setUp(self):
    super(TestNsBigSqliteMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsBigSqliteMemorized, self).tearDown()
