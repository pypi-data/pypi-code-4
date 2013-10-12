# -*- coding: utf8 -*-
from . import TestCase
from inxpect import expect
from inxpect import getters


class ListMethodTest(TestCase):
    def setUp(self):
        get_attr = getters.AttrByName('attribute')
        class Expect(object):
            attribute = expect.List(get_attr)
        self.expect = Expect()
        class Tested(object):
            attribute = ['value1','value2','value3',['value4']]
        self.object = Tested()

    def test_at_returns_a_function_that_tests_value_list_index(self):
        test = self.expect.attribute.at(1).equal_to('value2')
        self.assertTrue(test(self.object))

    def test_at_can_be_called_twice(self):
        test = self.expect.attribute.at(3).at(0).equal_to('value4')
        self.assertTrue(test(self.object))

    def test_has_returns_a_function_to_test_value_in_list(self):
        test_true = self.expect.attribute.has('value')
        test_false = self.expect.attribute.at(3).has('value4')
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_len_returns_a_function_to_make_tests_on_list_len(self):
        test_true = self.expect.attribute.len == 4
        self.assertTrue(test_true(self.object))

    def test_has_all_returns_a_function_to_test_all_values_in_list(self):
        test_true = self.expect.attribute.has_all(['value1', 'value2', 'value3'])
        test_false = self.expect.attribute.at(3).has_all(['value4', 'value1'])
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_any_returns_a_function_to_test_any_values_in_list(self):
        test_true = self.expect.attribute.has_any(['value', 'value4', 'value5'])
        test_false = self.expect.attribute.at(3).has_any(['value4', 'value1'])
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_has_key_returns_a_function_to_test_key_in_list(self):
        test_true = self.expect.attribute.has_key(0)
        test_false = self.expect.attribute.at(3).has_key(1)
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_keys_returns_a_function_to_test_keys_in_list(self):
        test_true = self.expect.attribute.has_keys([3, 0, 1])
        test_false = self.expect.attribute.at(3).has_keys([0, 2])
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_any_keys_returns_a_function_to_test_keys_in_list(self):
        test_true = self.expect.attribute.has_any_key([6, 4, 12])
        test_false = self.expect.attribute.at(3).has_any_key([0, 1])
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))
