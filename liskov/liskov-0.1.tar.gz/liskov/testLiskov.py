# -*- coding: utf8 -*-
import unittest
from liskov import subtypeof, behave_as, can_substitute


class LiskovSubstitutionTest(unittest.TestCase):

    def test_can_substitute_decorator_create_new_subtype(self):
        @can_substitute('fixtures.calc.BasicCalc', 'fixtures.convert.BasesConvert')
        class ScientificCalc(object):
            pass

        from fixtures.calc import BasicCalc
        from fixtures.convert import BasesConvert
        assert issubclass(ScientificCalc, (BasicCalc, BasesConvert))


    def test_substitute_metaclass_create_new_subtype(self):
        class ScientificCalc(object):
            __metaclass__ = behave_as('fixtures.calc.BasicCalc', 'fixtures.convert.BasesConvert')

        from fixtures.calc import BasicCalc
        from fixtures.convert import BasesConvert
        assert issubclass(ScientificCalc, (BasicCalc, BasesConvert))


    def test_subtypeof_import_a_class_in_nested_scope(self):
        class ScientificCalc(subtypeof('fixtures.calc.BasicCalc')):
            pass

        from fixtures.calc import BasicCalc
        assert issubclass(ScientificCalc, BasicCalc)

