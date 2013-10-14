# -*- coding: utf8 -*-
from . import TestCase
from inxpect.expect.property import DefaultProperty
from inxpect.expect.operator import Operator

class EqualMinusOne(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return (given - 1) == expected

class ShouldTest(TestCase):
    def test_it_permits_to_give_your_own_operators(self):
        prop = DefaultProperty()
        equal_11 = prop.should(EqualMinusOne, 10)

        self.assertTrue(equal_11(11))
        self.assertFalse(equal_11(10))

    def test_it_has_compare_magic_methods(self):
        prop = DefaultProperty()
        equal_10 = prop.should == 10

        self.assertTrue(equal_10(10))
        self.assertFalse(equal_10(11))

    def test_compare_methods_can_take_tuple_with_expect_and_closure(self):
        mod_2 = lambda num: num % 2
        prop = DefaultProperty()
        multiple_of_2 = prop.should == (0, mod_2)

        self.assertTrue(multiple_of_2(10))
        self.assertFalse(multiple_of_2(11))

class ShouldNotTest(TestCase):
    def test_it_permits_to_give_your_own_operators(self):
        prop = DefaultProperty()
        not_equal_11 = prop.should_not(EqualMinusOne, 10)

        self.assertTrue(not_equal_11(10))
        self.assertFalse(not_equal_11(11))

    def test_it_has_compare_magic_methods(self):
        prop = DefaultProperty()
        not_equal_10 = prop.should_not == 10

        self.assertTrue(not_equal_10(11))
        self.assertFalse(not_equal_10(10))

    def test_compare_methods_can_take_tuple_with_expect_and_closure(self):
        mod_2 = lambda num: num % 2
        prop = DefaultProperty()
        not_multiple_of_2 = prop.should_not == (0, mod_2)

        self.assertTrue(not_multiple_of_2(11))
        self.assertFalse(not_multiple_of_2(10))

