# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import os.path
import sqlite3
import hashlib
from datetime import datetime as d


import MySQLdb as mysql

from . import TestCase, mysqlConfig
from base import NotFoundError, IntegrityError
from ns import NestedSetsTree
from compat.mysqldb import Mysqldb as MysqlWrapper
from compat.sqlite3 import Sqlite3 as SqliteWrapper


class TestNsBigMysql(TestCase):
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    
    super(TestNsBigMysql, self).setUp()
    self.testee = NestedSetsTree(self.db, 'big', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
  
  def hashEdges(self):
    '''Hashes comared to another tree implementation'''
    
    cursor = self.db.cursor()
    cursor.execute('''
      SELECT node_id, parent_id 
      FROM big
      ORDER BY l ASC
    ''')
    
    s = ''
    result = hashlib.md5()
    for r in cursor:
      result.update('({0},{1})'.format(*r))
      s += '({0},{1})'.format(*r)
    
    return result.hexdigest()
  
  def testAdd(self):
    nodeId = self.testee.add(dict(value = 123), parentId = 20889)
    self.testee.validate(True)
    self.assertTrue(self.testee.isDescendantOf(1, nodeId))
    self.assertTrue(self.testee.isDescendantOf(20889, nodeId))
    
    nodeId = self.testee.add(dict(value = 98), prevId = 20387)
    self.testee.validate(True)
    self.assertTrue(self.testee.isDescendantOf(1, nodeId))
    self.assertTrue(self.testee.isDescendantOf(self.testee.getNode(20387)['parentId'], nodeId))
  
  def testMove(self):
    self.testee.move(21598, parentId = 30421)
    self.testee.validate(True)
    self.assertEqual('3fd7e06752a0df6fe7dbd1651c88b8d8', self.hashEdges())
    
    self.testee.move(19896, prevId = 30938)
    self.testee.validate(True)
    self.assertEqual('571540c1b6b24b91fff8bbccc4c19ba5', self.hashEdges())
  
  def testRemove(self):
    self.testee.remove(29959)
    self.testee.validate(True)
    self.assertEqual('cdf0b5a6756fda2aaf729840cd6184e4', self.hashEdges())
    
    self.testee.remove(30820)
    self.testee.validate(True)
    self.assertEqual('8d0fa84ee5389a869f0c4115e75d6e1e', self.hashEdges())
  
  def testEdit(self):
    self.testee.edit(30925, {
      'parentId' : 1,
      'nodeId'   : 123, 
      'right'    : 1244,
      'left'     : 12445,
      'number'   : 198
    })
    
    self.assertEqual({
      'nodeId'   : 30925, 
      'parentId' : 29795,
      'left'     : 33, 
      'right'    : 52, 
      'number'   : 198 
    }, self.testee.getNode(30925))
  
  def testGetRoot(self):
    self.assertEqual({
      'nodeId'   : 1, 
      'parentId' : None, 
      'left'     : 1,
      'right'    : 6806, 
      'number'   : 177 
    }, self.testee.getRoot())
    
  def testGetNode(self):
    self.assertEqual({
      'nodeId'   : 1, 
      'parentId' : None, 
      'left'     : 1,
      'right'    : 6806, 
      'number'   : 177
    }, self.testee.getNode(1))
    
    self.assertEqual({
      'nodeId'   : 20167, 
      'parentId' : 20136, 
      'left'     : 5846,
      'right'    : 5847, 
      'number'   : 32
    }, self.testee.getNode(20167))
    
    self.assertRaises(NotFoundError, self.testee.getNode, 65489)
    self.assertRaises(NotFoundError, self.testee.getNode, None)
    
  def testGetParent(self):
    self.assertEqual({
      'nodeId'   : 30925, 
      'parentId' : 29795, 
      'left'     : 33,
      'right'    : 52, 
      'number'   : 239
    }, self.testee.getParent(30933))

    self.assertEqual({
      'nodeId'   : 30907, 
      'parentId' : 30906, 
      'left'     : 67,
      'right'    : 90, 
      'number'   : 254
    }, self.testee.getParent(30918))
    
    self.assertRaises(NotFoundError, self.testee.getParent, 1)
    self.assertRaises(NotFoundError, self.testee.getParent, None)

  def testGetPrevious(self):
    self.assertEqual({
      'nodeId'   : 30938, 
      'parentId' : 30935, 
      'left'     : 26,
      'right'    : 27, 
      'number'   : 145
    }, self.testee.getPrevious(30937))
    
    self.assertEqual(30888, self.testee.getPrevious(30887)['nodeId'])
    self.assertEqual(30874, self.testee.getPrevious(30873)['nodeId'])
    
    for id in (1, 30875, 30819, 30816, 30811, 30797):
      self.assertRaises(NotFoundError, self.testee.getPrevious, id)
      
  def testGetNext(self):
    self.assertEqual({
      'nodeId'   : 30727, 
      'parentId' : 30717, 
      'left'     : 451,
      'right'    : 452, 
      'number'   : 37
    }, self.testee.getNext(30728))
    
    self.assertEqual(30537, self.testee.getNext(30650)['nodeId'])
    self.assertEqual(30632, self.testee.getNext(30633)['nodeId'])
    
    for id in (1, 30638, 30594, 30560, 30561, 30551):
      self.assertRaises(NotFoundError, self.testee.getNext, id)

  def testGetPath(self):
    self.assertEqual([
      {'parentId' : None,  'right' : 6806, 'nodeId' : 1,     'number' : 177, 'left' : 1}, 
      {'parentId' : 1,     'right' : 2311, 'nodeId' : 29795, 'number' : 137, 'left' : 18}, 
      {'parentId' : 29795, 'right' : 52,   'nodeId' : 30925, 'number' : 239, 'left' : 33}, 
      {'parentId' : 30925, 'right' : 37,   'nodeId' : 30933, 'number' : 224, 'left' : 36}
    ], self.testee.getPath(30933))
    
    self.assertEqual([1], [n['nodeId'] for n in self.testee.getPath(1)])
    self.assertEqual(
      [1, 29795, 30905, 30906, 30907, 30918], 
      [n['nodeId'] for n in self.testee.getPath(30918)]
    )
    
  def testGetChildren(self):
    self.assertEqual([
      {'parentId' : 1, 'right' : 17,   'nodeId' : 2,     'number' : 143, 'left' : 2}, 
      {'parentId' : 1, 'right' : 2311, 'nodeId' : 29795, 'number' : 137, 'left' : 18}, 
      {'parentId' : 1, 'right' : 6805, 'nodeId' : 19685, 'number' : 105, 'left' : 2312}
    ], self.testee.getChildren(1))
    
    self.assertEqual([
      {'parentId' : 30907, 'right' : 69, 'nodeId' : 30918, 'number' : 119, 'left' : 68}, 
      {'parentId' : 30907, 'right' : 71, 'nodeId' : 30917, 'number' : 131, 'left' : 70}, 
      {'parentId' : 30907, 'right' : 73, 'nodeId' : 30916, 'number' : 93,  'left' : 72},
      {'parentId' : 30907, 'right' : 75, 'nodeId' : 30915, 'number' : 111, 'left' : 74}, 
      {'parentId' : 30907, 'right' : 77, 'nodeId' : 30914, 'number' : 70,  'left' : 76}, 
      {'parentId' : 30907, 'right' : 79, 'nodeId' : 30913, 'number' : 164, 'left' : 78}, 
      {'parentId' : 30907, 'right' : 81, 'nodeId' : 30912, 'number' : 80,  'left' : 80}, 
      {'parentId' : 30907, 'right' : 83, 'nodeId' : 30911, 'number' : 164, 'left' : 82}, 
      {'parentId' : 30907, 'right' : 85, 'nodeId' : 30910, 'number' : 161, 'left' : 84}, 
      {'parentId' : 30907, 'right' : 87, 'nodeId' : 30909, 'number' : 129, 'left' : 86}, 
      {'parentId' : 30907, 'right' : 89, 'nodeId' : 30908, 'number' : 76,  'left' : 88}
    ], self.testee.getChildren(30907))
    
    self.assertEqual([], self.testee.getChildren(21617))
    
  def testGetDescendants(self):
    self.assertEqual([
      {'parentId' : 21613, 'right' : 2944, 'nodeId' : 21617, 'number' : 90,  'left' : 2943}, 
      {'parentId' : 21613, 'right' : 2946, 'nodeId' : 21616, 'number' : 37,  'left' : 2945}, 
      {'parentId' : 21613, 'right' : 2948, 'nodeId' : 21615, 'number' : 116, 'left' : 2947}, 
      {'parentId' : 21613, 'right' : 2950, 'nodeId' : 21614, 'number' : 181, 'left' : 2949}
    ], self.testee.getDescendants(21613))
    
    self.assertEqual([
      {'parentId' : 2,    'right' : 16, 'nodeId' : 3,    'number' : 183, 'left' : 3}, 
      {'parentId' : 3,    'right' : 15, 'nodeId' : 1006, 'number' : 232, 'left' : 4}, 
      {'parentId' : 1006, 'right' : 14, 'nodeId' : 1007, 'number' : 101, 'left' : 5}, 
      {'parentId' : 1007, 'right' : 13, 'nodeId' : 1008, 'number' : 66,  'left' : 6}, 
      {'parentId' : 1008, 'right' : 12, 'nodeId' : 1009, 'number' : 25,  'left' : 7}, 
      {'parentId' : 1009, 'right' : 11, 'nodeId' : 1010, 'number' : 184, 'left' : 8}, 
      {'parentId' : 1010, 'right' : 10, 'nodeId' : 1019, 'number' : 81,  'left' : 9}
    ], self.testee.getDescendants(2))
    
    self.assertEqual([], self.testee.getDescendants(21617))

  def testIsDescendantOf(self):
    self.assertFalse(self.testee.isDescendantOf(1019, 1))
    self.assertFalse(self.testee.isDescendantOf(1019, 1019))
    self.assertFalse(self.testee.isDescendantOf(29795, 21668))
    
    self.assertTrue(self.testee.isDescendantOf(1, 1019))
    self.assertTrue(self.testee.isDescendantOf(2, 1019))
    self.assertTrue(self.testee.isDescendantOf(3, 1019))
    self.assertTrue(self.testee.isDescendantOf(1006, 1019))
    self.assertTrue(self.testee.isDescendantOf(1007, 1019))
    self.assertTrue(self.testee.isDescendantOf(1010, 1019))
    
    self.assertRaises(NotFoundError, self.testee.isDescendantOf, 1, 65489)
    self.assertRaises(NotFoundError, self.testee.isDescendantOf, 65489, 1)
  
  def testIsLeaf(self):
    self.assertFalse(self.testee.isLeaf(1))
    self.assertFalse(self.testee.isLeaf(2))
    self.assertFalse(self.testee.isLeaf(3))
    self.assertFalse(self.testee.isLeaf(1006))
    self.assertFalse(self.testee.isLeaf(1007))
    self.assertFalse(self.testee.isLeaf(1008))
    self.assertFalse(self.testee.isLeaf(1009))
    self.assertFalse(self.testee.isLeaf(1010))
    
    self.assertTrue(self.testee.isLeaf(1019))
    self.assertTrue(self.testee.isLeaf(30522))
    self.assertTrue(self.testee.isLeaf(30515))
    self.assertTrue(self.testee.isLeaf(30941))
    self.assertTrue(self.testee.isLeaf(21898))
    
    self.assertRaises(NotFoundError, self.testee.isLeaf, 65489)
    
  def testValidate(self):
    self.assertEqual('fe6ded7cd5d951f54b8ace3219a57247', self.hashEdges())

    
    self.testee.validate()

    
    self.db.cursor().execute('''
      UPDATE big
      SET l = 6805
      WHERE node_id IN(20785, 21804)
    ''')
    
    message = 'Left must always be less than right: \(20785L?, 21804L?\)'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
    
  def testValidateEdges(self):
    self.testee.validate(True)
    
    
    self.db.cursor().execute('''
      UPDATE big
      SET parent_id = 1
      WHERE node_id IN(19705, 20231)
    ''')
    
    message = ('Adjacency list edges do not match nested sets edges: '
      '((19705L?, 1L?), (19705L?, 19690L?), (20231L?, 1L?), (20231L?, 20209L?))')
    message = message.replace('(', '\(').replace(')', '\)')
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate, True)
  
  def testMemorize(self):
    s = d.now()
    for c in (None, 8, 128, 1024):
      memoryTree = self.testee.memorize(chunk = c)
      memoryTree.columns['nodeId'] = 'node_id'
      self.assertEqual(self.testee.getRoot(), memoryTree.getRoot())
      self.assertEqual(self.testee.getDescendants(1), memoryTree.getDescendants(1))
      
      print c, d.now() - s
      s = d.now()


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
    
  def testMethodCoverage(self):
    pass


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
