# -*- coding: utf-8 -*- 
from __future__ import unicode_literals

from unittest import TestCase

import six

from microfilters import Filter, FilterSet


class TestFilter(TestCase):

    def test_sanitize(self):
        self.assertEqual('foo', Filter().sanitize('foo'))

    def test_filter(self):
        self.assertEqual(['list', 'of', 'strings'], Filter().filter(['list', 'of', 'strings'], 'list'))


class TestFilterSet(TestCase):

    def test_constructor(self):
        with self.assertRaises(Exception):
            FilterSet('foo')

    def test_sanitize(self):
        self.assertEqual('foo', FilterSet({'this': Filter()}).sanitize('foo'))

    def test_filter(self):
        self.assertEqual(['list', 'of', 'strings'], FilterSet({'this': Filter()}).filter(['list', 'of', 'strings'], {'this': 'list'}))


class TestSimpleImplementation(TestCase):

    def setUp(self):

        self.item_list = ['lukas', 'peter' , 'barbara', 'eventually']

        class StringListFilter(Filter):

            def sanitize(self, value):
                if not isinstance(value, six.text_type):
                    raise Exception
                return value

            def filter(self, item_list, value):
                return list(filter(lambda x: value in x, item_list))

        self.filter_set = FilterSet({
            'first': StringListFilter(),
            'second': StringListFilter(),
            'third': StringListFilter(),
        })

    def test_filter(self):

        value_dict = {
            'first': 'u'
        }
        expected = ['lukas', 'eventually']
        result = self.filter_set.filter(self.item_list, value_dict)
        self.assertEqual(expected, result)

    def test_additional_filter(self):

        value_dict = {
            'first': 'a',
            'second': 'r'
        }
        expected = ['barbara']
        result = self.filter_set.filter(self.item_list, value_dict)
        self.assertEqual(expected, result)

    def test_invalid_value(self):

        value_dict = {
            'first': 'a',
            'second': 2
        }
        with self.assertRaises(Exception):
            self.filter_set.filter(self.item_list, value_dict)

