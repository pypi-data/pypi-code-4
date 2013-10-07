from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testNumericalityValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_numericality_validator(self):
        from minos.validators import NumericalityValidator

        foo = testClass(
            bignum=25,
            smallnum=4,
            floatnum=3.14,
            notnum='apple',
            strnum='3'
        )

        gte_validator1 = NumericalityValidator('bignum', greater_than_or_equal_to=25)
        gte_validator2 = NumericalityValidator('smallnum', greater_than_or_equal_to=10)

        self.assertEqual(gte_validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, gte_validator2.validate_wrapper, foo)

        lte_validator1 = NumericalityValidator('bignum', less_than_or_equal_to=10)
        lte_validator2 = NumericalityValidator('smallnum', less_than_or_equal_to=10)

        self.assertRaises(ValidationError, lte_validator1.validate_wrapper, foo)
        self.assertEqual(lte_validator2.validate_wrapper(foo), None)

        gt_validator1 = NumericalityValidator('bignum', greater_than=10)
        gt_validator2 = NumericalityValidator('smallnum', greater_than=10)

        self.assertEqual(gt_validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, gt_validator2.validate_wrapper, foo)

        lt_validator1 = NumericalityValidator('bignum', less_than=10)
        lt_validator2 = NumericalityValidator('smallnum', less_than=10)

        self.assertRaises(ValidationError, lt_validator1.validate_wrapper, foo)
        self.assertEqual(lt_validator2.validate_wrapper(foo), None)

        equal_validator1 = NumericalityValidator('bignum')
        equal_validator2 = NumericalityValidator('smallnum')

        self.assertEqual(equal_validator1.validate_wrapper(foo), None)
        self.assertEqual(equal_validator2.validate_wrapper(foo), None)

        int_validator1 = NumericalityValidator('bignum', only_integer=True)
        int_validator2 = NumericalityValidator('floatnum', only_integer=True)

        self.assertEqual(int_validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, int_validator2.validate_wrapper, foo)

        str_num_validator = NumericalityValidator('strnum')
        not_num_validator = NumericalityValidator('notnum')

        self.assertEqual(str_num_validator.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, not_num_validator.validate_wrapper, foo)
