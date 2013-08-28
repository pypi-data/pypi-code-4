# coding: utf-8
import tempfile
import unittest

from gat_games.game_engine.gat_json import *


class Normal(object):
    def __init__(self):
        self.a = 1


class JSONTests(unittest.TestCase):
    def test_encode_object(self):
        encoded_object = encode_object(Normal())
        self.assertEquals(encoded_object, dict(a=1))

    def test_dump(self):
        obj = dict(a='b', c=1)
        fd, filepath = tempfile.mkstemp(text=True)
        fd = open(filepath, 'w')
        string = dump(obj, fd, sort_keys=True)
        fd = open(filepath, 'r')
        self.assertEquals(fd.read(), '{"a": "b", "c": 1}')

    def test_dumps(self):
        obj = dict(a='b', c=1)
        string = dumps(obj, sort_keys=True)
        self.assertEquals(string, '{"a": "b", "c": 1}')

    def test_load(self):
        string = '{"a": "b", "c": 1}'
        fd, filepath = tempfile.mkstemp(text=True)
        fd = open(filepath, 'w')
        fd.write(string)
        fd.close()
        fd = open(filepath, 'r')
        obj = load(fd)
        self.assertEquals(obj, dict(a='b', c=1))

    def test_loads(self):
        string = '{"a": "b", "c": 1}'
        obj = loads(string)
        self.assertEquals(obj, dict(a='b', c=1))

    def test_loads_dumps(self):
        obj = dict(a='b', c=1)
        string = dumps(obj)
        obj2 = loads(string)
        self.assertEquals(obj, obj2)
