# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Tests for the pyojo package.

assertEqual(a, b)     a == b      
assertNotEqual(a, b)     a != b      
assertTrue(x)     bool(x) is True      
assertFalse(x)     bool(x) is False      
assertIs(a, b)     a is b     2.7
assertIsNot(a, b)     a is not b     2.7
assertIsNone(x)     x is None     2.7
assertIsNotNone(x)     x is not None     2.7
assertIn(a, b)     a in b     2.7
assertNotIn(a, b)     a not in b     2.7
assertIsInstance(a, b)     isinstance(a, b)     2.7
assertNotIsInstance(a, b)     not isinstance(a, b)     2.7

"""
import pyojo
import unittest
from base import main, BasicTestCase
from test_js import *
from test_dojo import *
from test_dijit import *

# ----------------------------------------------------------------------------

    

class TestArray(BasicTestCase):
    def setUp(self):
        self.store = pyojo.data.Array()
                
    def test_attr(self):
        self.store.a = 1
        assert self.store.a==1
        assert self.store["a"]==1

class TestDOM(BasicTestCase):
    def setUp(self):
        self.root = pyojo.js.DOM(href="URL")
        self.root.add("level1", object)
        self.root["level1"].add("level2", object)
        
    def test_node_creation(self):
        assert type(self.root["level1"])==type(self.root)
        self.assertIsInstance(self.root["level1"], pyojo.js.DOM)
        self.assertEqual(self.root["level1"].name, "level1", 'incorrect Node.name')
        self.assertEqual(self.root["level1"].cls.__name__, "object", 'incorrect Node.cls')
        self.assertTrue(self.root["level1"] in self.root.children)
        with self.assertRaises(Exception):
            self.root["level1"] = object
        
    def test_node_prop(self): 
        #with self.assertRaises(Exception):
        #    self.root.prop = "test"
        self.assertIsInstance(self.root.prop, dict)
        self.assertEqual(self.root.prop["href"], "URL", 'incorrect Node.prop')
        self.root.prop["href"]="URL-2"
        self.assertEqual(self.root.prop["href"], "URL-2", 'incorrect Node.prop')


# ----------------------------------------------------------------------------
        
if __name__=='__main__': 
    main()

# ----------------------------------------------------------------------------
