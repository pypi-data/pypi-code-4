#:coding=utf8:

from unittest import TestCase

from decimal import Decimal

from beproud.utils.decimalutils import *

class TestDecimalUtils(TestCase):

    def assertDecimalValue(self, d, val):
        self.assertTrue(isinstance(d, Decimal))
        self.assertEqual(d, Decimal(val))
  
    def test_force_decimal_string(self):
        for val in ["1.04949", "9", "-1.04"]:
            self.assertDecimalValue(force_decimal(val), val)
        
        for val in ["val", u"日本語"]:
            try:
                dec = force_decimal(val)
            except ValueError:
                pass
            else:
                self.fail("Expected failure for %s" % val)

    def test_numbers_only(self):
        for val in ["1.04949", "9", "-1.04"]:
            self.assertDecimalValue(force_decimal(val, numbers_only=True), val)
        
        for val in ["val", u"日本語"]:
            self.assertEqual(force_decimal(val, numbers_only=True), val)
