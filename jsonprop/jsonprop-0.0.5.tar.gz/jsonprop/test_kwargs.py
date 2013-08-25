from json_field import json_field
from json_dict import JsonObject
import unittest

class MyClass(JsonObject):
    json_test = json_field('json_test_prop', 'foo', False)

class JsonFieldTests(unittest.TestCase):

    def test_kwargs(self):
        myclass = MyClass( json_test = 'bar' )

        expected = {'json_test_prop': 'bar'}
        actual = myclass._to_json_dict()

        self.assertEqual(actual, expected) 

