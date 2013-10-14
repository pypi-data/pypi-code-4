# -*- coding: utf8 -*-
from . import TestCase, Mock
from inxpect.expect.property import DefaultProperty
from inxpect import getters


class DefaultPropertyTest(TestCase):
    def setUp(self):
        class Expect(object):
            attribute = DefaultProperty(getters.AttrByName('attribute'))

        class Tested(object):
            attribute = 'value'

        self.expect = Expect()
        self.object = Tested()

    def test_equal_to_returns_a_function_to_test_equality(self):
        test_true = self.expect.attribute.equal_to('value')
        test_false = self.expect.attribute.equal_to('val')
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_not_equal_to_returns_a_function_to_test_inequality(self):
        test_true = self.expect.attribute.not_equal_to('value')
        test_false = self.expect.attribute.not_equal_to('val')
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_lower_than_returns_a_function_to_test_lowerity(self):
        self.object.attribute = 10
        test_true = self.expect.attribute.lower_than(10)
        test_false = self.expect.attribute.lower_or_equal_than(10)
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_greater_than_returns_a_function_to_test_greaterity(self):
        self.object.attribute = 20
        test_true = self.expect.attribute.greater_than(20)
        test_false = self.expect.attribute.greater_or_equal_than(20)
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))


    def test_same_as_returns_a_function_to_test_identity(self):
        expected = Mock()
        not_expected = Mock()
        self.object.attribute = expected
        test_true = self.expect.attribute.same_as(expected)
        test_false = self.expect.attribute.same_as(not_expected)
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_not_same_as_returns_a_function_to_test_non_identity(self):
        expected = Mock()
        not_expected = Mock()
        self.object.attribute = expected
        test_true = self.expect.attribute.not_same_as(expected)
        test_false = self.expect.attribute.not_same_as(not_expected)
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_type_is_not_returns_a_function_to_test_type_inequality(self):
        test_true = self.expect.attribute.type_is_not(type(''))
        test_false = self.expect.attribute.type_is_not(type(1))
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_instance_of_returns_a_function_to_test_isinstance(self):
        self.object.attribute = Mock()
        test_true = self.expect.attribute.instance_of((Mock, DefaultProperty))
        test_false = self.expect.attribute.instance_of(int)
        self.assertTrue(test_true(self.object))
        self.assertFalse(test_false(self.object))

    def test_not_instance_of_returns_a_function_to_test_is_not_instance(self):
        self.object.attribute = Mock()
        test_true = self.expect.attribute.not_instance_of((Mock, DefaultProperty))
        test_false = self.expect.attribute.not_instance_of(int)
        self.assertFalse(test_true(self.object))
        self.assertTrue(test_false(self.object))

    def test_len_returns_a_function_to_make_tests_on_len(self):
        test_true = self.expect.attribute.len >= 5
        self.assertTrue(test_true(self.object))
