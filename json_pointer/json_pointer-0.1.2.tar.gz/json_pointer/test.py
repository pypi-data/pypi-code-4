import os
import json
import re
import types
import copy
import glob
import unittest

from json_pointer import Pointer, PointerSyntaxError, PointerError

FILES = glob.glob(
    os.path.join(os.path.dirname(__file__), 'test-suite/*.json')
)


def to_function_name(string):
    """
    Turn an string into a valid function name
    """
    return re.sub(r'\W+', '_', string.lower())


class TestJSONPointer(unittest.TestCase):
    """
    Test case for JSONPointer. `test_` methods are automatically added from test-suite
    """
    document = {
        "foo": ["bar", "baz"],
        "": 0,
        "a/b": 1,
        "c%d": 2,
        "e^f": 3,
        "g|h": 4,
        "i\\j": 5,
        "k\"l": 6,
        " ": 7,
        "~1": 8,
        "m~n": 9
    }

    def test_get(self):
        pointers = {
            "/foo/-": None,
            "/foo": ["bar", "baz"],
            "/foo/0": "bar",
            "/": 0,
            "/a~1b": 1,
            "/c%d": 2,
            "/e^f": 3,
            "/g|h": 4,
            "/i\\j": 5,
            "/k\"l": 6,
            "/ ": 7,
            "/~01": 8,
            "/m~0n": 9,
        }

        for pointer, expected_value in pointers.items():
            self.assertEqual(
                Pointer(pointer).get(self.document),
                expected_value
            )

    def test_syntax_error(self):
        self.assertRaises(
            PointerSyntaxError,
            Pointer,
            'bla'
        )

    def test_get_error(self):
        pointers = [
            "/foo/-/1",
            "/bar",
            "/foo/2"
        ]

        for pointer in pointers:
            self.assertRaises(
                PointerError,
                Pointer(pointer).get,
                self.document
            )

    def test_set(self):
        pointers = [
            "/foo",
            "/foo/0",
            "/foo/2",
            "/",
            "/a~1b",
            "/c%d",
            "/e^f",
            "/g|h",
            "/i\\j",
            "/k\"l",
            "/ ",
            "/m~0n",
        ]

        for pointer in pointers:
            document = copy.deepcopy(self.document)
            pointer = Pointer(pointer)
            pointer.set(document, 'bla')
            self.assertEqual(
                pointer.get(document), 'bla'
            )
        
    def test_set_dash(self):
        pointer = '/foo/-'
        document = copy.deepcopy(self.document)
        pointer = Pointer(pointer)
        pointer.set(document, 'bla')

        self.assertEqual(
            document['foo'][-1], 'bla'
        )
        
    def test_unset(self):
        pointers = [
            "/foo",
            "/",
            "/a~1b",
            "/c%d",
            "/e^f",
            "/g|h",
            "/i\\j",
            "/k\"l",
            "/ ",
            "/m~0n",
        ]

        for pointer in pointers:
            document = copy.deepcopy(self.document)
            pointer = Pointer(pointer)

            pointer.unset(document)
            self.assertRaises(
                PointerError,
                pointer.get,
                document
            )
        

