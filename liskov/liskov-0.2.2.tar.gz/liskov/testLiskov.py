# -*- coding: utf8 -*-
import sys
import unittest

from .liskov import behave_as, can_substitute, subtype, append_sys_path, constrain, under_constraint

import os.path
__dir__ = os.path.dirname(os.path.abspath(__file__))
append_sys_path(os.path.join(__dir__, 'fixtures'))

import elephant


class LiskovSubstitutionTest(unittest.TestCase):

    def test_can_substitute_decorator_create_new_subtype(self):
        @can_substitute('calc.BasicCalc', 'convert.BasesConvert')
        class ScientificCalc(object):
            pass

        from calc import BasicCalc
        from convert import BasesConvert
        assert issubclass(ScientificCalc, (BasicCalc, BasesConvert))


    def test_behave_as_metaclass_create_new_subtype(self):
        CalcConvert = behave_as('calc.BasicCalc', 'convert.BasesConvert')
        if sys.version < '3':
            class ScientificCalc(object):
                __metaclass__ = CalcConvert
        else:
            ScientificCalc = CalcConvert('ScientificCalc', (object, ), {})

        from calc import BasicCalc
        from convert import BasesConvert
        assert issubclass(ScientificCalc, (BasicCalc, BasesConvert))


    def test_subtypeof_import_a_class_in_nested_scope(self):
        class ScientificCalc(subtype('calc.BasicCalc')):
            pass

        from calc import BasicCalc
        assert issubclass(ScientificCalc, BasicCalc)

class ConstrainedSubtypeTest(unittest.TestCase):
    def test_can_substitute_except_constraints(self):
        @can_substitute('elephant.ElephantTest')
        @under_constraint('test_it_can_be_grey', 'test_it_can_be_white')
        class RoyalElephantTest(object):
            def new_elephant(self, color):
                return elephant.RoyalElephant(color)

        self.__run(RoyalElephantTest)

    def test_behave_as_except_constraints(self):
        ElephantTest = behave_as('elephant.ElephantTest').except_for('test_it_can_be_grey', 'test_it_can_be_white')
        if sys.version < '3':
            class RoyalElephantTest(object):
                __metaclass__ = ElephantTest

                def new_elephant(self, color):
                    return elephant.RoyalElephant(color)
        else:
            def new_elephant(self, color):
                return elephant.RoyalElephant(color)
            RoyalElephantTest = ElephantTest('RoyalElephantTest', (object, ), {'new_elephant': new_elephant})

        self.__run(RoyalElephantTest)

    def test_subtypeof_except_constraints(self):
        class RoyalElephantTest(subtype('elephant.ElephantTest') & constrain('test_it_can_be_grey', 'test_it_can_be_white')):
            def new_elephant(self, color):
                return elephant.RoyalElephant(color)

        self.__run(RoyalElephantTest)

    def __run(self, testCase):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(testCase)
        suite.debug()

if __name__ == "__main__":
    unittest.main()
