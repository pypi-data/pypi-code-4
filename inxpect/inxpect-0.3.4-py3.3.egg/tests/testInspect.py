# -*- coding: utf8 -*-
from . import TestCase
from inxpect.inspect import expect_factory, use_DefaultMethod
from inxpect import expect


class Callable(int):
    kwargs = {'kwarg1': 'val1'}
    args1 = ('arg1', 'arg2')
    def __call__(self, *args, **kwargs):
        pass

class Inspected(object):
    attr1 = ['val1', 'val2']
    attr2 = {}
    attr3 = None
    attr4 = Callable()
    def func1(self):
        pass
    @staticmethod
    def func2(self):
        pass
    @classmethod
    def func3(self):
        pass

class InspectTest(TestCase):
    def filter_public_members(self, expected):
        return [value for value in dir(expected) if value[0] != '_' and not value.endswith('Item')]

    def test_build_returns_an_object_with_same_properties_as_class(self):
        expected = expect_factory(Inspected)
        public_members = self.filter_public_members(expected)
        self.assertEqual(['attr1', 'attr2', 'attr3', 'attr4'], public_members)


    def test_build_returns_an_object_with_same_properties_as_object(self):
        inspected = Inspected()
        expected = expect_factory(inspected)
        public_members = self.filter_public_members(expected)
        self.assertEqual(['attr1', 'attr2', 'attr3', 'attr4'], public_members)

    def test_built_object_properties_are_List_when_object_ones_are_list(self):
        expected = expect_factory(Inspected)
        self.assertIsInstance(expected.attr1, expect.List)

    def test_built_object_properties_getter_is_AttrByName(self):
        expected = expect_factory(Inspected)
        test = Inspected()
        assertion = expected.attr1.equal_to(['val1', 'val2'])
        self.assertTrue(assertion(test))

    def test_built_object_properties_are_Dict_when_object_ones_are_dict(self):
        expected = expect_factory(Inspected)
        self.assertIsInstance(expected.attr2, expect.Dict)

    def test_built_object_properties_are_expect_factory_object_when_object_ones_are_objects(self):
        expected = expect_factory(Inspected, 1)
        self.assertIsInstance(expected.attr4.kwargs, expect.Dict)

    def test_built_object_properties_are_DefaultMethod_for_builtin(self):
        expected = expect_factory(Inspected)
        self.assertIsInstance(expected.attr3, expect.Expect)

    def test_for_list_and_dict_add_ItemMethod(self):
        expected = expect_factory(Inspected)
        self.assertIsInstance(expected.attr1Item, expect.ListItem)
        self.assertIsInstance(expected.attr2Item, expect.DictItem)

    def test_for_list_and_dict_ItemMethod_name_is_singular_of_property_if_end_by_s(self):
        expected = expect_factory(Inspected, 1)
        self.assertIsInstance(expected.attr4.kwarg, expect.DictItem)

    def test_tuple_are_treaten_as_list(self):
        expected = expect_factory(Inspected, 1)
        self.assertIsInstance(expected.attr4.args1, expect.List)


class IsDefaultMethodTest(TestCase):
    def test_strings_are_DefaultMethod(self):
        self.assertTrue(use_DefaultMethod('dqsklj'))
    def test_numbers_are_DefaultMethod(self):
        self.assertTrue(use_DefaultMethod(10.2))
    def test_booleans_are_DefaultMethod(self):
        self.assertTrue(use_DefaultMethod(True))
    def test_NoneType_is_DefaultMethod(self):
        self.assertTrue(use_DefaultMethod(None))
    def test_object_type_is_not_DefaultMethod(self):
        self.assertFalse(use_DefaultMethod(object))
    def test_Class_are_not_DefaultMethod(self):
        self.assertFalse(use_DefaultMethod(Callable))
    def test_object_are_not_DefaultMethod(self):
        self.assertFalse(use_DefaultMethod(object()))
