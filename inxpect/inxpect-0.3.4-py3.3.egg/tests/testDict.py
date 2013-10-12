# -*- coding: utf8 -*-
from . import TestCase
from inxpect import expect
from inxpect import getters


class DictTest(TestCase):
    def setUp(self):
        get_attr = getters.AttrByName('attribute')
        class Expect(object):
            attribute = expect.Dict(get_attr)
        self.expect = Expect()
        class Tested(object):
            attribute = {'key1':['value1'], 'key2':'value2', 'key3':'value3'}
        self.object = Tested()

    def test_at_returns_a_function_that_tests_value_dict_index(self):
        test = self.expect.attribute.at('key2').equal_to('value2')
        self.assertTrue(test(self.object))

    def test_at_can_be_called_twice(self):
        test = self.expect.attribute.at('key1').at(0).equal_to('value1')
        self.assertTrue(test(self.object))

    def test_has_item_returns_a_function_to_test_value_in_dict(self):
        test_true = self.expect.attribute.has_item('key', 'value1')
        test_false = self.expect.attribute.has_item('key3', 'value3')
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_len_returns_a_function_to_make_tests_on_dict_len(self):
        test_true = self.expect.attribute.len <= 3
        self.assertTrue(test_true(self.object))

    def test_has_items_returns_a_function_to_test_all_items_in_dict(self):
        test_true = self.expect.attribute.has_items({'key2':'value2', 'key3':'value3'})
        test_false = self.expect.attribute.has_items({'key1':'value4', 'key2':'value2'})
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_any_item_returns_a_function_to_test_any_item_in_dict(self):
        test_true = self.expect.attribute.has_any_item({'key':'value', 'key2':'value', 'key3':'value2'})
        test_false = self.expect.attribute.has_any_item({'key4': 'value4', 'key1': ['value1']})
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_has_key_returns_a_function_to_test_key_in_list(self):
        test_true = self.expect.attribute.has_key('key1')
        test_false = self.expect.attribute.has_key('key4')
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_keys_returns_a_function_to_test_keys_in_list(self):
        test_true = self.expect.attribute.has_keys(['key3', 'key1', 'key2'])
        test_false = self.expect.attribute.has_keys(['key1', 'key4'])
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_any_keys_returns_a_function_to_test_keys_in_list(self):
        test_true = self.expect.attribute.has_any_key(['key', 'key11', 'key12'])
        test_false = self.expect.attribute.has_any_key(['key1', 'key0'])
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_has_value_returns_a_function_to_test_value_in_list(self):
        test_true = self.expect.attribute.has_value('value2')
        test_false = self.expect.attribute.has_value('value4')
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_values_returns_a_function_to_test_values_in_list(self):
        test_true = self.expect.attribute.has_values(['value3', ['value1'], 'value2'])
        test_false = self.expect.attribute.has_values(['value1', 'value4'])
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_has_any_values_returns_a_function_to_test_values_in_list(self):
        test_true = self.expect.attribute.has_any_value(['val', 'val1', 'val2'])
        test_false = self.expect.attribute.has_any_value(['value2', 3])
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

