from __future__ import absolute_import

import unittest
from minos.errors import ValidationError


class testWithValidator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_email_validator(self):
        from minos.validators import WithValidator

        class testClass:
            fruit_info = None

            def __init__(self, fruit_info):
                self.fruit_info = fruit_info

            def ripeness(self):
                return self.fruit_info['ripe'] == True

            def yellowness(self):
                return self.fruit_info['fruit_type'] in ['banana', 'grapefruit', 'lemon']

        foo = testClass(
            fruit_info={
                'fruit_type': 'apple',
                'ripe': True
            }
        )

        validator1 = WithValidator('fruit_info', with_='ripeness')
        validator2 = WithValidator('fruit_info', with_='yellowness')

        self.assertEqual(validator1.validate_wrapper(foo), None)
        self.assertRaises(ValidationError, validator2.validate_wrapper, foo)

