from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testEmailValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_email_validator(self):
        from minos.validators import EmailValidator

        foo = testClass(
            email='thisisanemail@gmail.com',
            email2='maybethisisanemail@msu.edu',
            not_an_email='oh hai'
        )

        validator1 = EmailValidator('email')
        validator2 = EmailValidator('email2')
        validator3 = EmailValidator('not_an_email')

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertEqual(validator2.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator3.validate_wrapper, foo)

