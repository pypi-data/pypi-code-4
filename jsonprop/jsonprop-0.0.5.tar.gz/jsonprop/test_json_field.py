from json_field import json_field
from json_dict import JsonObject
import unittest

class MyClass(JsonObject):
    json_test = json_field('json_test_prop', 'foo', False)
    def __init__(self):
		pass

class MyClass2(JsonObject):
    json_test = json_field('json_test_prop')
    def __init__(self):
		pass

class JsonFieldTests(unittest.TestCase):
    def test_default(self):
        myclass = MyClass()

        expected = {'json_test_prop': 'foo'}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 

    def test_defaults(self):
        myclass2 = MyClass2()
        expected = {'json_test_prop': None}
        actual = myclass2._to_json_dict()

        self.assertEqual(actual, expected) 
		
    def test_override_default(self):
        myclass = MyClass()
        myclass.json_test = 'bar'
        expected = {'json_test_prop': 'bar'}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 
