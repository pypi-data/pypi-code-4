from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class testJSONValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_json_validator(self):
        from minos.validators import JSONValidator

        foo = testClass(
            jsontext=u'{"a": 1, "c": true, "b": "true", "d": "2013-02-18T12:44:07.065691"}',
            not_json='the quick brown fox grabbed an uber."'
        )

        validator1 = JSONValidator('jsontext')
        validator2 = JSONValidator('not_json')

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator2.validate_wrapper, foo)

