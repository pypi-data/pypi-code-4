'''
Created on Dec 23, 2011

@author: Nicklas Boerjesson
'''
import unittest
from ube.api.tree.node import node
from qal.dal.tests.framework import default_dal
from ube.concerns.connection import set_connection

from qal.dal.dal_types import DB_POSTGRESQL
from unittest.case import skip

@default_dal(DB_POSTGRESQL)
class Test(unittest.TestCase):
    _dal = None   
    _new_node1 = None
    _new_node2 = None
    def setUp(self):
        '''The tests are only run towards one database backend, default is Postgres, 
        to run against any other backend, simply change the database type in the 
        default_dal decorator.  ''' 
        set_connection(self._dal)
        Test._dal = self._dal
        from ube.api.tree.access import access
        Test._access = access()

        
    def tearDown(self):
        pass
        
    def test_1_create_node(self):
        Test._new_node1 = Test._access.create_new(None, 1101, "Test broker1")
        self.assertEqual(Test._new_node1.IP_address, "0.0.0.0")
        Test._new_node2 = Test._access.create_new(None, 1201, "Test broker2")
        self.assertEqual(Test._new_node2.IP_address, "0.0.0.0")  
    def test_2_save_node(self):
        Test._new_node1.Description = "Test broker1 Description"
        Test._new_node2.Description = "Test broker2 Description"
        Test._access.save_nodes([Test._new_node1, Test._new_node2])
        Test._new_node1.Description = "Test broker1 Description v.2"
        Test._new_node2.Description = "Test broker2 Description v.2"
        Test._access.save_nodes([Test._new_node1, Test._new_node2])
      
    def test_3_load_node(self):
        _cmp_node = Test._access.load_nodes([Test._new_node1.nodeid], _with_data = True)[0]
        self.assertEqual(_cmp_node.Description, Test._new_node1.Description)
        self.assertEqual(_cmp_node.nodeuuid, Test._new_node1.nodeuuid)
        
    def test_4_delete_node(self):
        Test._access.delete_nodes([Test._new_node1, Test._new_node2])

        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()