# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import os.path
import sqlite3

import MySQLdb as mysql

from . import TestCase, mysqlConfig, visualize
from base import NotFoundError, IntegrityError
from ns import NestedSetsTree
from compat.mysqldb import Mysqldb as MysqlWrapper
from compat.sqlite3 import Sqlite3 as SqliteWrapper


class TestNsSmallMysql(TestCase):
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    
    super(TestNsSmallMysql, self).setUp()
    
    self.testee = NestedSetsTree(self.db, 'small', ('name',))
    self.testee.columns['nodeId'] = 'node_id'

  def pprint(self):
    print visualize(self.testee)

  def dump(self):
    cursor = self.db.cursor()
    cursor.execute('''
      SELECT node_id, parent_id, l, r, name 
      FROM small
      ORDER BY l ASC
    ''')
    return tuple(cursor)

  def testAdd(self):
    self.db.cursor().execute('DELETE FROM small')
    
    rootId = self.testee.add({'name' : 'NR'}, None, None)
    print self.dump()
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual({
      'nodeId'   : rootId, 
      'parentId' : None,
      'left'     : 1, 
      'right'    : 2, 
      'name'     : u'NR' 
    }, self.testee.getRoot())
    self.assertEqual(((rootId, None, 1,  2, 'NR'),), self.dump())

  def testAddToC1(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  15, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  14, 'B3'),
      (7,    6, 10, 13, 'C1'),
      [None, 7, 11, 12, 'D1'],
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'D1'), parentId = 7)
    self.testee.validate(True)
    self.pprint()
    
    expected[7][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())

  def testAddBehindC1(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  15, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  14, 'B3'),
      (7,    6, 10, 11, 'C1'),
      [None, 6, 12, 13, 'C2'],
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'C2'), prevId = 7)
    self.testee.validate(True)
    self.pprint()
    
    expected[7][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
    
  def testAddToA2(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  15, 'A2'),
      [None, 4, 7,  8,  'B5'],
      (5,    4, 9,  10, 'B2'),
      (6,    4, 11, 14, 'B3'),
      (7,    6, 12, 13, 'C1'),
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'B5'), parentId = 4)
    self.testee.validate(True)
    self.pprint()
    
    expected[4][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
  
  def testAddBehindA2(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  13, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      [None, 1, 14, 15, 'A4'],
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'A4'), prevId = 4)
    self.testee.validate(True)
    self.pprint()
    
    expected[7][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
    
  def testAddBehindB2(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  15, 'A2'),
      (5,    4, 7,  8,  'B2'),
      [None, 4, 9,  10, 'B5'],
      (6,    4, 11, 14, 'B3'),
      (7,    6, 12, 13, 'C1'),
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'B5'), prevId = 5)
    self.testee.validate(True)
    self.pprint()
    
    expected[5][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
  
  def testAddBehindB3(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  15, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      [None, 4, 13, 14, 'B5'],
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'B5'), prevId = 6)
    self.testee.validate(True)
    self.pprint()
    
    expected[7][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
  
  def testAddBehindB4(self):
    expected = (
      (1, None, 1,  20, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  13, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      (8,    1, 14, 19, 'A3'), 
      (9,    8, 15, 16, 'B4'),
      [None, 8, 17, 18, 'B5']
    )
    
    id = self.testee.add(dict(name = 'B5'), prevId = 9)
    self.testee.validate(True)
    self.pprint()
    
    expected[9][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
  
  def testAddToR(self):
    expected = (
      (1, None, 1,  20, 'R'),
      [None, 1, 2,  3,  'A4'],
      (2,    1, 4,  7,  'A1'),
      (3,    2, 5,  6,  'B1'),
      (4,    1, 8,  15, 'A2'),
      (5,    4, 9,  10, 'B2'),
      (6,    4, 11, 14, 'B3'),
      (7,    6, 12, 13, 'C1'),
      (8,    1, 16, 19, 'A3'), 
      (9,    8, 17, 18, 'B4')
    )
    
    id = self.testee.add(dict(name = 'A4'), parentId = 1)
    self.testee.validate(True)
    self.pprint()
    
    expected[1][0] = id
    expected = tuple(map(tuple, expected))
    
    self.assertEqual(expected, self.dump())
  
  def testAddBehindR(self):
    message = 'Cannot add node behind root'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.add, dict(name = 'RR'), prevId = 1)
    
  def testMove(self):
    message = 'Cannot move node into self'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 4, prevId = 6)
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 6, parentId = 6)
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 6, prevId = 7)
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 1, prevId = 8)
    
    message = 'Cannot move node under its own descendant'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 1, parentId = 6)
    self.assertRaisesRegexp(IntegrityError, message, self.testee.move, 1, prevId = 7)
    
    message = 'No node with id:19'
    self.assertRaisesRegexp(NotFoundError, message, self.testee.move, 19, prevId = 7)
    self.assertRaisesRegexp(NotFoundError, message, self.testee.move, 1, parentId = 19)
    self.assertRaisesRegexp(NotFoundError, message, self.testee.move, 1, prevId = 19)
    
    message = 'No node with id:None'
    self.assertRaisesRegexp(NotFoundError, message, self.testee.move, 2, prevId = 1)
  
  def testMoveB1ToR(self):
    self.testee.move(3, parentId = 1)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (3,    1, 2,  3,  'B1'),
      (2,    1, 4,  5,  'A1'),
      (4,    1, 6,  13, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveB1ToA1(self):
    '''pass'''
    
    self.testee.move(3, parentId = 2)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  13, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveB1BehindA2(self):
    self.testee.move(3, prevId = 4)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  3,  'A1'),
      (4,    1, 4,  11, 'A2'),
      (5,    4, 5,  6,  'B2'),
      (6,    4, 7,  10, 'B3'),
      (7,    6, 8,   9, 'C1'),
      (3,    1, 12, 13, 'B1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveB3ToB1(self):
    self.testee.move(6, parentId = 3)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  9,  'A1'),
      (3,    2, 3,  8,  'B1'),
      (6,    3, 4,  7,  'B3'),
      (7,    6, 5,  6,  'C1'),
      (4,    1, 10, 13, 'A2'),
      (5,    4, 11, 12, 'B2'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())

  def testMoveA2BehindA1(self):
    '''pass'''
    
    self.testee.move(4, prevId = 2)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  13, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  12, 'B3'),
      (7,    6, 10, 11, 'C1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveA2ToA1(self):
    self.testee.move(4, parentId = 2)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  13, 'A1'),
      (4,    2, 3,  10, 'A2'),
      (5,    4, 4,  5,  'B2'),
      (6,    4, 6,  9,  'B3'),
      (7,    6, 7,  8,  'C1'),
      (3,    2, 11, 12, 'B1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveA2ToR(self):
    self.testee.move(4, parentId = 1)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (4,    1, 2,   9, 'A2'),
      (5,    4, 3,   4, 'B2'),
      (6,    4, 5,   8, 'B3'),
      (7,    6, 6,   7, 'C1'),
      (2,    1, 10, 13, 'A1'),
      (3,    2, 11, 12, 'B1'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testMoveA2ToB4(self):
    self.testee.move(4, parentId = 9)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,   5, 'A1'),
      (3,    2, 3,   4, 'B1'),
      (8,    1, 6,  17, 'A3'), 
      (9,    8, 7,  16, 'B4'),
      (4,    9, 8,  15, 'A2'),
      (5,    4, 9,  10, 'B2'),
      (6,    4, 11, 14, 'B3'),
      (7,    6, 12, 13, 'C1'),
    ), self.dump())
  
  def testMoveA3ToC1(self):
    self.testee.move(8, parentId = 7)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  17, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  16, 'B3'),
      (7,    6, 10, 15, 'C1'),
      (8,    7, 11, 14, 'A3'), 
      (9,    8, 12, 13, 'B4')
    ), self.dump())
  
  def testMoveA3BehindB2(self):
    self.testee.move(8, prevId = 5)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  17, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (8,    4, 9,  12, 'A3'), 
      (9,    8, 10, 11, 'B4'),
      (6,    4, 13, 16, 'B3'),
      (7,    6, 14, 15, 'C1'),
    ), self.dump())
  
  def testMoveC1BehindB4(self):
    self.testee.move(7, prevId = 9)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  11, 'A2'),
      (5,    4, 7,  8,  'B2'),
      (6,    4, 9,  10, 'B3'),
      (8,    1, 12, 17, 'A3'), 
      (9,    8, 13, 14, 'B4'),
      (7,    8, 15, 16, 'C1'),
    ), self.dump())
  
  def testMoveA3BehindA1(self):
    self.testee.move(8, prevId = 2)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (8,    1, 6,  9,  'A3'), 
      (9,    8, 7,  8,  'B4'),
      (4,    1, 10, 17, 'A2'),
      (5,    4, 11, 12, 'B2'),
      (6,    4, 13, 16, 'B3'),
      (7,    6, 14, 15, 'C1'),
    ), self.dump())
  
  def testMoveB2BehindB3(self):
    self.testee.move(5, prevId = 6)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  18, 'R'),
      (2,    1, 2,  5,  'A1'),
      (3,    2, 3,  4,  'B1'),
      (4,    1, 6,  13, 'A2'),
      (6,    4, 7,  10, 'B3'),
      (7,    6, 8,  9,  'C1'),
      (5,    4, 11, 12, 'B2'),
      (8,    1, 14, 17, 'A3'), 
      (9,    8, 15, 16, 'B4')
    ), self.dump())
  
  def testRemove(self):
    sql = 'SELECT COUNT(*) FROM small'
    cursor = self.db.cursor()

    cursor.execute(sql)
    self.assertEqual(9, cursor.fetchone()[0])
    
    self.testee.remove(1)
    self.testee.validate(True)
    self.pprint()
    
    cursor.execute(sql)
    self.assertEqual(0, cursor.fetchone()[0])
  
  def testRemoveA2(self):
    self.testee.remove(4)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1, 10, 'R'), 
      (2, 1,    2, 5,  'A1'), 
      (3, 2,    3, 4,  'B1'), 
      (8, 1,    6, 9,  'A3'), 
      (9, 8,    7, 8,  'B4')
    ), self.dump())
  
  def testRemoveB3(self):
    self.testee.remove(6)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  14, 'R'), 
      (2, 1,    2,  5,  'A1'), 
      (3, 2,    3,  4,  'B1'), 
      (4, 1,    6,  9,  'A2'), 
      (5, 4,    7,  8,  'B2'), 
      (8, 1,    10, 13, 'A3'), 
      (9, 8,    11, 12, 'B4')
    ), self.dump())

  def testRemoveA1(self):
    self.testee.remove(2)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  14, 'R'), 
      (4, 1,    2,  9,  'A2'), 
      (5, 4,    3,  4,  'B2'), 
      (6, 4,    5,  8,  'B3'), 
      (7, 6,    6,  7,  'C1'), 
      (8, 1,    10, 13, 'A3'), 
      (9, 8,    11, 12, 'B4')
    ), self.dump())
  
  def testRemoveB4(self):
    self.testee.remove(9)
    self.testee.validate(True)
    self.pprint()
    
    self.assertEqual((
      (1, None, 1,  16, 'R'), 
      (2, 1,    2,  5,  'A1'), 
      (3, 2,    3,  4,  'B1'), 
      (4, 1,    6,  13, 'A2'), 
      (5, 4,    7,  8,  'B2'), 
      (6, 4,    9,  12, 'B3'), 
      (7, 6,    10, 11, 'C1'),       
      (8, 1,    14, 15, 'A3') 
    ), self.dump())
    
  def testIsDescendantOf(self):
    for id in range(2, 10):
      self.assertTrue(self.testee.isDescendantOf(1, id))
    for id in (5, 6, 7):
      self.assertTrue(self.testee.isDescendantOf(4, id))
    self.assertTrue(self.testee.isDescendantOf(2, 3))
    self.assertTrue(self.testee.isDescendantOf(6, 7))
    self.assertTrue(self.testee.isDescendantOf(8, 9))
    
    for id in range(1, 10):
      self.assertFalse(self.testee.isDescendantOf(id, id))
      
    for id in set(range(1, 10)) - set((3,)):
      self.assertFalse(self.testee.isDescendantOf(2, id))
    for id in set(range(1, 10)) - set((5, 6, 7)):
      self.assertFalse(self.testee.isDescendantOf(4, id))
    for id in set(range(1, 10)) - set((7,)):
      self.assertFalse(self.testee.isDescendantOf(6, id))
    for id in set(range(1, 10)) - set((9,)):
      self.assertFalse(self.testee.isDescendantOf(8, id))
      
    for leafId in (3, 5, 7, 9):
      for id in range(1, 10):
        self.assertFalse(self.testee.isDescendantOf(leafId, id))
    
    self.assertRaises(NotFoundError, self.testee.isDescendantOf, 1, 65489)
    self.assertRaises(NotFoundError, self.testee.isDescendantOf, 65489, 1)
  
  def testIsLeaf(self):
    for id in (1, 2, 4, 6, 8):
      self.assertFalse(self.testee.isLeaf(id))
      
    for id in (3, 5, 7, 9):
      self.assertTrue(self.testee.isLeaf(id))
  
  def testGetParent(self):
    self.assertEqual({
      'nodeId'   : 4, 
      'parentId' : 1, 
      'left'     : 6,
      'right'    : 13, 
      'name'     : 'A2'
    }, self.testee.getParent(6))

    self.assertEqual(self.testee.getRoot(), self.testee.getParent(2))
    
    self.assertRaises(NotFoundError, self.testee.getParent, 1)
    self.assertRaises(NotFoundError, self.testee.getParent, None)
    
  def testGetPrevious(self):
    self.assertEqual({
      'nodeId'   : 4, 
      'parentId' : 1, 
      'left'     : 6,
      'right'    : 13, 
      'name'     : 'A2'
    }, self.testee.getPrevious(8))
    
    self.assertEqual('B2', self.testee.getPrevious(6)['name'])
    self.assertEqual('A1', self.testee.getPrevious(4)['name'])
    
    for id in (1, 2, 3, 5, 7, 9):
      self.assertRaises(NotFoundError, self.testee.getPrevious, id)
      
  def testGetNext(self):
    self.assertEqual({
      'nodeId'   : 4, 
      'parentId' : 1, 
      'left'     : 6,
      'right'    : 13, 
      'name'     : 'A2'
    }, self.testee.getNext(2))
    
    self.assertEqual('A3', self.testee.getNext(4)['name'])
    self.assertEqual('B3', self.testee.getNext(5)['name'])
    
    for id in (1, 3, 6, 7, 8, 9):
      self.assertRaises(NotFoundError, self.testee.getNext, id)
  
  def testGetNode(self):
    self.assertEqual({
      'nodeId'   : 1, 
      'parentId' : None, 
      'left'     : 1,
      'right'    : 18, 
      'name'     : 'R'
    }, self.testee.getNode(1))
    self.assertEqual(self.testee.getRoot(), self.testee.getNode(1))
    
    self.assertEqual({
      'nodeId'   : 8, 
      'parentId' : 1, 
      'left'     : 14,
      'right'    : 17, 
      'name'     : 'A3'
    }, self.testee.getNode(8))
    
    self.assertRaises(NotFoundError, self.testee.getNode, 65489)
    self.assertRaises(NotFoundError, self.testee.getNode, None)
  
  def testGetRoot(self):
    self.assertEqual({
      'nodeId'   : 1, 
      'parentId' : None, 
      'left'     : 1,
      'right'    : 18, 
      'name'     : 'R' 
    }, self.testee.getRoot())
  
  def testGetPath(self):
    self.assertEqual([
      {'nodeId' : 1, 'parentId' : None, 'left' : 1,  'right' : 18, 'name' : 'R'}, 
      {'nodeId' : 4, 'parentId' : 1,    'left' : 6,  'right' : 13, 'name' : 'A2'}, 
      {'nodeId' : 6, 'parentId' : 4,    'left' : 9,  'right' : 12, 'name' : 'B3'}, 
      {'nodeId' : 7, 'parentId' : 6,    'left' : 10, 'right' : 11, 'name' : 'C1'}
    ], self.testee.getPath(7))
    
    self.assertEqual([1], [n['nodeId'] for n in self.testee.getPath(1)])
    self.assertEqual([1, 2], [n['nodeId'] for n in self.testee.getPath(2)])
    self.assertEqual([1, 4, 5], [n['nodeId'] for n in self.testee.getPath(5)])
    self.assertEqual([1, 8, 9], [n['nodeId'] for n in self.testee.getPath(9)])
    
    self.assertRaises(NotFoundError, self.testee.getPath, 65489)
   
  def testEdit(self):
    self.testee.edit(4, {
      'nodeId'   : 123, 
      'parentId' : 10,
      'right'    : 1244,
      'left'     : 12445,
      'name'     : 'A2-2'
    })
    
    self.assertEqual({
      'nodeId'   : 4,  # no change 
      'parentId' : 1,  # no change
      'left'     : 6,  # no change 
      'right'    : 13, # no change
      'name'     : 'A2-2'
    }, self.testee.getNode(4))
  
  def testGetChildren(self):
    self.assertEqual([
      {'nodeId' : 5, 'parentId' : 4, 'left' : 7, 'right' : 8,  'name' : 'B2'},
      {'nodeId' : 6, 'parentId' : 4, 'left' : 9, 'right' : 12, 'name' : 'B3'} 
    ], self.testee.getChildren(4))
    
    self.assertEqual([
      {'nodeId' : 2, 'parentId' : 1, 'left' : 2, 'right'  : 5,  'name' : 'A1'},
      {'nodeId' : 4, 'parentId' : 1, 'left' : 6, 'right'  : 13, 'name' : 'A2'},
      {'nodeId' : 8, 'parentId' : 1, 'left' : 14, 'right' : 17, 'name' : 'A3'} 
    ], self.testee.getChildren(1))
    
    self.assertEqual([], self.testee.getChildren(9))
    self.assertEqual([], self.testee.getChildren(65489))
  
  def testGetDescendants(self):
    self.assertEqual([
      {'nodeId' : 5, 'parentId' : 4, 'left' : 7,  'right' : 8,  'name' : 'B2'},
      {'nodeId' : 6, 'parentId' : 4, 'left' : 9,  'right' : 12, 'name' : 'B3'}, 
      {'nodeId' : 7, 'parentId' : 6, 'left' : 10, 'right' : 11, 'name' : 'C1'} 
    ], self.testee.getDescendants(4))
    
    self.assertEqual([
      {'nodeId' : 9, 'parentId' : 8, 'left' : 15, 'right' : 16,  'name' : 'B4'},
    ], self.testee.getDescendants(8))
    
    self.assertEqual(range(2, 10), [n['nodeId'] for n in self.testee.getDescendants(1)])
    
    self.assertEqual([], self.testee.getDescendants(9))
    self.assertEqual([], self.testee.getDescendants(65489))

  def testValidate(self):
    self.testee.validate()
    
    self.db.cursor().execute('DELETE FROM small')
    self.testee.validate()
    
  def testValidateLeftMustAlwaysBeLessThanRight(self):
    self.db.cursor().execute('''
      UPDATE small
      SET l = 11
      WHERE node_id IN(5, 7)
    ''')
    
    message = 'Left must always be less than right: \(5L?, 7L?\)'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateTreeMustHaveNoLoops(self):
    self.db.cursor().execute('''
      UPDATE small
      SET parent_id = node_id
      WHERE node_id IN(1, 9)
    ''')
    
    message = 'Tree must have no loops: \(1L?, 9L?\)'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateMinLeftMustAlwaysBe1(self):
    self.db.cursor().execute('''
      UPDATE small
      SET l = l + 1
      WHERE node_id = 1
    ''')
    
    message = 'Min left must always be 1'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateMaxRightMustAlwaysBeNumberOfNodes2(self):
    self.db.cursor().execute('''
      UPDATE small
      SET r = r + 2
      WHERE node_id = 1
    ''')
    
    message = 'Max right must always be number of nodes / 2'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
    
  def testValidateMaxRightMustAlwaysBeNumberOfNodes2Extra(self):
    self.db.cursor().execute('''
      INSERT INTO small(parent_id, l, r, name) 
      VALUES(NULL, 4, 5, 'Bad')
    ''')
    
    message = 'Max right must always be number of nodes / 2'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateTreeMustHaveOneRoot(self):
    values = dict(name = 'RR')
    target = self.testee.getNode(1)
    parentId = target['parentId']
    prev     = target['right']
    self.testee._updateMarkup(prev, 2)
    
    values['parentId'] = parentId
    values['left']     = prev + 1;
    values['right']    = prev + 2;
    
    sql = '''
      INSERT INTO small({fields}) 
      VALUES({values})
    '''
    
    meta           = self.testee._getMeta()
    meta['fields'] = ','.join(v for k, v in self.testee.columns.items() if k in values)
    meta['values'] = ','.join(':{0}'.format(k) for k in self.testee.columns.keys() if k in values)
    
    cursor = self.db.cursor()
    cursor.execute(sql.format(**meta), values)
    
    message = 'Tree must have one root'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateParentOfRootMustBeNone(self):
    self.db.cursor().execute('''
      UPDATE small
      SET parent_id = 6
      WHERE node_id = 1
    ''')
    
    message = 'Parent of root must be none'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateRightMinusLeftMustAlwaysBeOdd(self):
    self.db.cursor().execute('''
      UPDATE small
      SET r = r + 1
      WHERE node_id IN(4, 5)
    ''')
    
    message = 'Right - left must always be odd: \(4L?, 5L?\)'
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateMarkupMustBeUniqueLeft(self):
    self.db.cursor().execute('''
      UPDATE small
      SET l = l - 2
      WHERE node_id IN(5, 9)
    ''')
    
    message = "Markup must be unique: \(\(u'(5,2|2,5)', 5L?\), \(u'(9,4|4,9)', 13L?\)\)"
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateMarkupMustBeUniqueRight(self):
    self.db.cursor().execute('''
      UPDATE small
      SET r = r + 2
      WHERE node_id IN(5, 9)
    ''')
    
    message = "Markup must be unique: \(\(u'(7,5|5,7)', 10L?\), \(u'(1,9|1,9)', 18L?\)\)"
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate)
  
  def testValidateAdjacencyListEdgesDoNotMatchNestedSetsEdges(self):
    self.db.cursor().execute('''
      UPDATE small
      SET parent_id = 1
      WHERE node_id IN(5, 7)
    ''')
    
    message = ('Adjacency list edges do not match nested sets edges: '
      '((5L?, 1L?), (5L?, 4L?), (7L?, 1L?), (7L?, 6L?))')
    message = message.replace('(', '\(').replace(')', '\)')
    self.assertRaisesRegexp(IntegrityError, message, self.testee.validate, True)

  def testMemorize(self):
    for c in range(16):
      memoryTree = self.testee.memorize(chunk = c)
      memoryTree.columns['nodeId'] = 'node_id'
      self.assertEqual(self.testee.getRoot(), memoryTree.getRoot())
      self.assertEqual(self.testee.getDescendants(1), memoryTree.getDescendants(1))


class TestNsSmallMysqlMemorized(TestNsSmallMysql):
  
  def setUp(self):
    super(TestNsSmallMysqlMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db 
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsSmallMysqlMemorized, self).tearDown()
    
  def testMethodCoverage(self):
    pass


class TestNsSmallSqlite(TestNsSmallMysql):
  
  def setUp(self):
    self.db = SqliteWrapper(sqlite3.connect(os.path.dirname(__file__) + '/fixture/sqlite.db'))
    
    TestCase.setUp(self)
    
    self.testee = NestedSetsTree(self.db, 'small', ('name',))
    self.testee.columns['nodeId'] = 'node_id'
  
  def testMethodCoverage(self):
    pass


class TestNsSmallSqliteMemorized(TestNsSmallSqlite):
  
  def setUp(self):
    super(TestNsSmallSqliteMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsSmallSqliteMemorized, self).tearDown()
