from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testLengthValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_length_validator(self):
        from minos.validators import LengthValidator

        foo = testClass(
            longtext="this is a longer sentence",
            shorttext="this"
        )

        gte_validator1 = LengthValidator('longtext', greater_than_or_equal_to=25)
        gte_validator2 = LengthValidator('shorttext', greater_than_or_equal_to=10)

        self.assertEqual(gte_validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, gte_validator2.validate_wrapper, foo)

        lte_validator1 = LengthValidator('longtext', less_than_or_equal_to=10)
        lte_validator2 = LengthValidator('shorttext', less_than_or_equal_to=10)

        self.assertRaises(ValidationError, lte_validator1.validate_wrapper, foo)
        self.assertEqual(lte_validator2.validate_wrapper(foo), None)

        gt_validator1 = LengthValidator('longtext', greater_than=10)
        gt_validator2 = LengthValidator('shorttext', greater_than=10)

        self.assertEqual(gt_validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, gt_validator2.validate_wrapper, foo)

        lt_validator1 = LengthValidator('longtext', less_than=10)
        lt_validator2 = LengthValidator('shorttext', less_than=10)

        self.assertRaises(ValidationError, lt_validator1.validate_wrapper, foo)
        self.assertEqual(lt_validator2.validate_wrapper(foo), None)

        equal_validator1 = LengthValidator('longtext', equal_to=10)
        equal_validator2 = LengthValidator('shorttext', equal_to=4)

        self.assertRaises(ValidationError, equal_validator1.validate_wrapper, foo)
        self.assertEqual(equal_validator2.validate_wrapper(foo), None)

