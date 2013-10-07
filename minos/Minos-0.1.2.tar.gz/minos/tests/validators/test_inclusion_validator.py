from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testInclusionValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_inclusion_validator(self):
        from minos.validators import InclusionValidator

        foo = testClass(
            bread='wheat'
        )

        validator1 = InclusionValidator('bread', in_=['sourdough', 'wheat', 'white', 'french'])
        validator2 = InclusionValidator('bread')
        validator3 = InclusionValidator('bread', in_=['challah', 'italian', 'seven grain'])

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertRaises(UserWarning, validator2.validate_wrapper, foo)
        self.assertRaises(ValidationError, validator3.validate_wrapper, foo)
