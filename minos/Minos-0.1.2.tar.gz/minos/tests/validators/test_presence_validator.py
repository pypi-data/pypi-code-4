from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testPresenceValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_presence_validator(self):
        from minos.validators import PresenceValidator

        foo = testClass(
            email='thisisanemail@gmail.com',
            email2='maybethisisanemail@msu.edu',
            empty=None,
        )

        validator1 = PresenceValidator('email')
        validator2 = PresenceValidator('email2')
        validator3 = PresenceValidator('empty')
        validator4 = PresenceValidator('narnia')

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertEqual(validator2.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator3.validate_wrapper, foo)
        self.assertRaises(ValidationError, validator4.validate_wrapper, foo)

