from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testMinimumPresenceValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_minimum_presence_validator(self):
        from minos.validators import MinimumPresenceValidator

        foo = testClass(
            apple=True
        )

        validator1 = MinimumPresenceValidator(['apple', 'orange', 'banana'])
        validator2 = MinimumPresenceValidator(['knife', 'spoon', 'fork'])

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator2.validate_wrapper, foo)
