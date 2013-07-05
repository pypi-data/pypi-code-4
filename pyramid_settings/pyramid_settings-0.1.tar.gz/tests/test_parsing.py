#-*- coding: utf-8 -*-
"""Tests for :mod:`eblight.helpers.dates`."""

from pyramid_settings import _parse_item


class TestDictParsing(object):

    def test_standard_int(self):
        assert _parse_item('ns', {'value1': 1}) == {'ns.value1': 1}

    def test_standard_str(self):
        assert _parse_item('ns', {'value1': '1'}) == {'ns.value1': '1'}

    def test_standard_None(self):
        assert _parse_item('ns', {'value1': None}) == {'ns.value1': None}

    def test_multi_base(self):
        td = _parse_item('ns', {'value1': None, 'value2': 2, 'value3': '3'})
        assert td == {'ns.value1': None, 'ns.value2': 2, 'ns.value3': '3'}

    def test_recursive(self):
        td = _parse_item('ns', {'value1': {'value2': {'value3': '3'}}})
        assert td == {'ns.value1.value2.value3': '3'}

    def test_tuple_in_dict(self):
        td = _parse_item('ns', {'value1': (1,2,3)})
        assert td == {'ns.value1': '1\n2\n3'}

    def test_list_in_dict(self):
        td = _parse_item('ns', {'value1': [1,None,3]})
        assert td == {'ns.value1': '1\nNone\n3'}


class TestIterableParsing(object):

    def test_list(self):
        td = _parse_item('name', [1,'2',None])
        assert td == {'name': '1\n2\nNone'}

    def test_tuple(self):
        td = _parse_item('name', (1,'2',None))
        assert td == {'name': '1\n2\nNone'}


class TestOtherParsing(object):

    def test_string(self):
        td = _parse_item('name', 'value')
        assert td == {'name': 'value'}

    def test_int(self):
        td = _parse_item('name', 1)
        assert td == {'name': 1}

    def test_callable(self):
        callble = lambda x: x
        td = _parse_item('name', callble)
        assert id(callble) == id(td['name'])
