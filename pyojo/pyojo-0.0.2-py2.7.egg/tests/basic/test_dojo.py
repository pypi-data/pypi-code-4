# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
from base import BasicTestCase
from pyojo.func import nolf
import pyojo.js as js
import pyojo.js.dojo as dojo

EXAMPLE = "alert('Test');"

class TestDojo(BasicTestCase):
    def setUp(self):
        self.x = dojo.Dojo()
                
    def test_class(self):
        self.assertIsInstance(self.x, js.Code)
        self.assertIsInstance(self.x, dojo.Dojo)
        assert str(type(self.x))=="<class 'pyojo.js.dojo._base.Dojo'>"

class TestMemory(BasicTestCase):
    def setUp(self):
        from pyojo.js.dojo.store import Memory
        self.x = Memory("name", {})

    def test_class(self):
        self.assertIsInstance(self.x, js.Dojo)
        assert str(type(self.x))=="<class 'pyojo.js.dojo.store.Memory'>"
        
class TestJsonRest(BasicTestCase):
    def setUp(self):
        from pyojo.js.dojo.store import JsonRest
        self.x = JsonRest()

    def test_class(self):
        self.assertIsInstance(self.x, js.Dojo)
        assert str(type(self.x))=="<class 'pyojo.js.dojo.store.JsonRest'>"

class Test_js_Dojo(BasicTestCase):
   
    def test_js_Dojo(self):
        example = js.Dojo(EXAMPLE)
        self.assertEqual(example.require, [])
        self.assertEqual(example.code(), EXAMPLE)                
        self.assertEqual(js.js_code(example), EXAMPLE)                
        self.assertEqual(nolf(js.get_code(example)), EXAMPLE)                
    
    def test_js_Dojo_require(self):
        example = js.Dojo(EXAMPLE).requires("dojo/ready")
        self.assertEqual(example.require, [])
        self.assertEqual(example._require, ["dojo/ready"])
        self.assertEqual(example.get_requires(), ["dojo/ready"])
        self.assertEqual(example.code(), EXAMPLE)                
        self.assertEqual(js.js_code(example), EXAMPLE)
    
    def test_js_Dojo_get_code(self):    
        example = js.Dojo(EXAMPLE).requires("dojo/ready")
        block = js.get_code(example)               
        self.assertIn("require(", block)                
        self.assertIn("['dojo/ready']", block)
        self.assertIn("function(ready)", block)
        self.assertIn("ready(", block)
        self.assertIn(EXAMPLE, block)
           