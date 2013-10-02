#!/usr/bin/env python
import unittest


def paramlen(*args):
    return len(args)


class Dummy(object):
    class_property_paramlen = paramlen

    @staticmethod
    def static_method_paramlen(*args):
        return paramlen(*args)

    def getlen_using_class(self, *args):
        allargs = [self]
        allargs.extend(args)
        return Dummy.class_property_paramlen(*allargs)

    def getlen_using_instance(self, *args):
        return self.class_property_paramlen(*args)

    def getlen_using_staticmethod_on_instance(self, *args):
        return self.static_method_paramlen(*args)

    def getlen_using_staticmethod_on_class(self, *args):
        return Dummy.static_method_paramlen(*args)


class test_callable_class_properties(unittest.TestCase):
    def setUp(self):
        self.dummyobj = Dummy()

    def _test_with_params(self, *args):
        classway = self.dummyobj.getlen_using_class(*args)
        instanceway = self.dummyobj.getlen_using_instance(*args)
        self.assertEqual(classway, instanceway)

    def _test_with_params_statically(self, *args):
        firstway = self.dummyobj.getlen_using_staticmethod_on_instance(*args)
        secondway = self.dummyobj.getlen_using_staticmethod_on_class(*args)
        self.assertEqual(firstway, secondway)

    def test_single_argument(self):
        self._test_with_params('dummy')
        self._test_with_params_statically('dummy')

    def test_no_params(self):
        self._test_with_params()
        self._test_with_params_statically()

    def test_with_multiple_parameters(self):
        self._test_with_params("a", 3, 4, self, 'monkey', dict())
        self._test_with_params_statically("a", 3, 4, self, 'monkey', dict())


class test_class_vs_instance_properties(unittest.TestCase):

    def setUp(self):
        class testclass(object):
            classprop = 1

            def __init__(self):
                self.instprop = 2

            def update_class_prop(self):
                self.classprop = 4

        class subclass(testclass):
            classprop = 2
        self.testclass = testclass
        self.subclass = subclass

    def test_that_class_property_can_be_called_using_dot_notation(self):
        inst = self.testclass()
        self.assertEqual(inst.classprop, 1)

    def test_that_instance_method_can_update_class_property(self):
        inst = self.testclass()
        inst.update_class_prop()
        self.assertEqual(inst.classprop, 4)

    def test_manual_update_of_class_property_affects_instance(self):
        inst = self.testclass()
        inst.classprop = 2
        self.assertEqual(inst.classprop, 2)

    def test_that_when_class_property_is_updated_doesnt_affect_others(self):
        inst = self.testclass()
        inst2 = self.testclass()
        inst.classprop = 3
        self.assertEqual(inst2.classprop, 1)

    def test_that_instance_method_doesnt_affect_other_instances(self):
        inst = self.testclass()
        inst2 = self.testclass()
        inst.update_class_prop()
        self.assertEqual(inst2.classprop, 1)

    def test_that_modifying_via_the_class_affects_instances(self):
        inst = self.testclass()
        self.testclass.classprop = 2
        self.assertEqual(inst.classprop, 2)

    def test_class_modifications_override_instance_modifications(self):
        inst = self.testclass()
        inst.classprop = 'banana'
        self.testclass.classprop = 0
        self.assertEqual(inst.classprop, 'banana')

    def test_that_modifying_subclass_prop_doesnt_affect_baseclass(self):
        self.subclass.classprop = 'banana'
        self.assertEqual(self.testclass.classprop, 1)
