from json_property import json_property   
from json_dict import JsonObject
import unittest


class MyClass(JsonObject):
    def __init__(self):
        self._test_prop = None

    @json_property('json_test_prop', False)
    def get_test_prop(self):
        return self._test_prop 

class MyClassSerializeNulls(JsonObject):
    def __init__(self):
        self._test_prop = None

    @json_property('json_test_prop', True)
    def get_test_prop(self):
        return self._test_prop 

class MyClassDefaults(JsonObject):
    def __init__(self):
        self._test_prop = None

    @json_property()
    def get_test_prop(self):
        return self._test_prop 

class MyJsonObjectClass(JsonObject):
    def __init__(self):
        self._test_prop = None

    @json_property('json_test_prop', False)
    def get_test_prop(self):
        return self._test_prop 

class JsonObjectTests(unittest.TestCase):
    def test_nominal(self):
        myclass = MyJsonObjectClass()
        myclass._test_prop = 'foo' 

        expected = {'json_test_prop': 'foo'}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 

    def test_json_dumps(self):
        myclass = MyJsonObjectClass()
        myclass._test_prop = 'foo' 

        expected = '{"json_test_prop": "foo"}'
        actual = myclass.json()

        self.assertEqual(actual, expected) 

    def test_json_defaults(self):
        myclass = MyClassDefaults()
        myclass._test_prop = 'foo' 

        expected = '{"get_test_prop": "foo"}'
        actual = myclass.json()

        self.assertEqual(actual, expected) 


class JsonPropertyTests(unittest.TestCase):

    def test_nominal(self):
        myclass = MyClass()
        myclass._test_prop = 'foo' 

        expected = {'json_test_prop': 'foo'}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 

    def test_excluded(self):
        myclass = MyClass()

        expected = {}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 
    
    def test_serialize_null(self):
        myclass = MyClassSerializeNulls()

        expected = {'json_test_prop': None}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 

