from __future__ import absolute_import

import unittest


class testValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_validator(self):
        from minos.validator import Validator

        test_validator = Validator(1, 2, 3, foo='bar', awesome=True)

        self.assertEqual(test_validator.args, (1, 2, 3))
        self.assertEqual(test_validator.kwargs, {'foo': 'bar', 'awesome': True})
