from __future__ import absolute_import

import unittest


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testDatetimeValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_datetime_validator(self):
        from minos.validators.datetime_validator import DatetimeValidator
        from minos.errors import ValidationError
        from datetime import datetime

        foo = testClass(datetyme=datetime.now(), not_a_datetime='ermahgerd datetimez!')
        validator1 = DatetimeValidator('datetyme')
        validator2 = DatetimeValidator('not_a_datetime')

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator2.validate_wrapper, foo)