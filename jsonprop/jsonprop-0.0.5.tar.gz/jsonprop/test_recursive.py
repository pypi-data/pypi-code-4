from json_field import json_field
from json_dict import JsonObject
import unittest

class MyClass(JsonObject):
    child = json_field('json_child', None, False)

class MyClass2(JsonObject):
    json_test = json_field('json_test_prop', 'foo', False)

class JsonFieldTests(unittest.TestCase):

    def test_kwargs(self):
        mychild = MyClass2()
        myparent = MyClass( child = mychild )

        expected = '{"json_child": {"json_test_prop": "foo"}}'
        actual = myparent.json()

        self.assertEqual(actual, expected) 

