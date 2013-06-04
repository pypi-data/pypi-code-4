# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import unittest
import types


mysqlConfig = {
  'host'    : '127.0.0.1',
  'user'    : 'guest',
  'passwd'  : '',
  'db'      : 'test_fangorn',
  'charset' : 'utf8'            
}


def visualize(tree, name = 'name'):
  sql = '''
    SELECT node.{nodeId}, node.{parentId}, node.{left}, node.{right}, node.{0}, COUNT(*)
    FROM {table} root
    JOIN {table} node ON node.{left} BETWEEN root.{left} AND root.{right}
    GROUP BY node.{nodeId}
    ORDER BY node.{left} ASC
  '''
  
  cursor = tree._db.cursor()
  cursor.execute(sql.format(name, **tree._getMeta()))
  
  return '\n'.join('{0}{1} {2}->{3} ({4}, {5})'.format(
    u'  ' * (r[5] - 2) + u'└─' if r[1] else '', r[4], r[0], r[1], r[2], r[3]
  ) for r in cursor)

class TestCase(unittest.TestCase):

  testee = None
  db     = None


  def setUp(self):
    if self.__class__ is TestCase:
      return
          
    self.db.begin()

  def tearDown(self):
    if self.__class__ is TestCase:
      return
    
    self.db.rollback()

  def testMethodCoverage(self):
    if self.__class__ is TestCase:
      return

    def methods(object):
      return {
        name for (name, value) in object.__class__.__dict__.items()
        if isinstance(value, types.FunctionType) and name[0] != '_'
      }

    self.assertFalse(self.testee is None, 'Testee must be created in setUp()')

    diff = set('test' + name[0].upper() + name[1:] for name in methods(self.testee)) - methods(self)
    self.assertEqual(0, len(diff), 'Test case misses: {0}'.format(', '.join(diff)))
