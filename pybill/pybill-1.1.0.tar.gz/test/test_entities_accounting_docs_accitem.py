# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs import AccItem


class AccItemTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.item = AccItem()
        
    def test_empty_object(self):
        """
        Tests an empty sold item contains nothing and has totals of 0.0
        """
        self.assertEqual(self.item.quantity, 0.0)
        self.assertEqual(self.item.quantity_digits, 0)
        self.assertEqual(self.item.unit_price, 0.0)
        self.assertEqual(self.item.unit_price_digits, ACCURACY)
        self.assertEqual(self.item.vat_rate, None)
        self.assertEqual(self.item.holdback_rate, None)
        self.assertEqual(self.item.holdback_on_vat, False)
        self.assertEqual(self.item.get_price(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.item.get_vat_amount(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.item.get_holdback_amount(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_price(self):
        """
        Tests the computation of the price (quantity * unit price)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.assertEqual(self.item.get_price(),
                          round(65.0, ACCURACY))

    def test_get_price_with_quantity_digits(self):
        """
        Tests the computation of the price (quantity * unit price) with a
        different number of digits for the quantity.
        """
        self.item.quantity = 5.1234
        self.item.quantity_digits = 2
        self.item.unit_price = 100.0
        self.assertEqual(self.item.get_price(),
                          round(512.00, ACCURACY))

    def test_get_price_with_unit_price_digits(self):
        """
        Tests the computation of the price (quantity * unit price) with a
        different number of digits for the unit price.
        """
        self.item.quantity = 50.0
        self.item.unit_price = 100.00438
        self.item.unit_price_digits = 4
        self.assertEqual(self.item.get_price(),
                          round(5000.22, ACCURACY))

    def test_get_price_with_holdback(self):
        """
        Tests the computation of the price when holdback rate is defined
        (quantity * unit price)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.holdback_rate = 5.0
        self.assertEqual(self.item.get_price(),
                          round(65.0, ACCURACY))

    def test_get_price_with_holdback_on_vat(self):
        """
        Tests the computation of the price when holdback rate on vat is defined
        (quantity * unit price)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_price(),
                          round(65.0, ACCURACY))

    def test_get_vat_amount(self):
        """
        Tests the computation of the vat amount
        (quantity * unit price * vat rate)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.assertEqual(self.item.get_vat_amount(),
                          round(12.74, ACCURACY))

    def test_get_vat_amount_with_no_vat(self):
        """
        Tests the computation of the vat amount when no vat rate is defined
        (quantity * unit price * vat rate)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.assertEqual(self.item.get_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_vat_amount_with_holdback(self):
        """
        Tests the computation of the vat amount when holdback rate is defined 
        (quantity * unit price * vat rate)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.assertEqual(self.item.get_vat_amount(),
                          round(12.74, ACCURACY))

    def test_get_vat_amount_with_holdback_on_vat(self):
        """
        Tests the computation of the vat amount when holdback rate on vat is
        defined 
        (quantity * unit price * vat rate)
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_vat_amount(),
                          round(12.74, ACCURACY))

    def test_get_including_taxes_price(self):
        """
        Tests the computation of the including taxes price
        (quantity * unit price * (1.0 + vat rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(77.74, ACCURACY))

    def test_get_including_taxes_price_with_no_vat(self):
        """
        Tests the computation of the including taxes price when no vat rate is
        defined
        (quantity * unit price * (1.0 + vat rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(65.0, ACCURACY))

    def test_get_including_taxes_price_with_holdback(self):
        """
        Tests the computation of the including taxes price when holdback rate is
        defined
        (quantity * unit price * (1.0 + vat rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(77.74, ACCURACY))

    def test_get_including_taxes_price_with_holdback_on_vat(self):
        """
        Tests the computation of the including taxes price when holdback rate
        on vat is defined
        (quantity * unit price * (1.0 + vat rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(77.74, ACCURACY))

    def test_get_holdback_with_no_holdback(self):
        """
        Tests the computation of the holdback when no holdback is defined
        (quantity * unit price * (holdback rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.assertEqual(self.item.get_holdback_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_with_holdback(self):
        """
        Tests the computation of the holdback when holdback is defined
        (quantity * unit price * (holdback rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.assertEqual(self.item.get_holdback_amount(),
                          round(3.25, ACCURACY))

    def test_get_holdback_with_holdback_on_vat(self):
        """
        Tests the computation of the holdback when holdback on vat is defined
        (quantity * unit price * (holdback rate) )
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_amount(),
                          round(3.25, ACCURACY))

    def test_get_holdback_vat_with_no_holdback(self):
        """
        Tests the computation of the vat holdback when no holdback is defined
        (quantity * unit price * vat_rate * (holdback rate) )
        if holdback_on_vat is True
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_vat_with_holdback(self):
        """
        Tests the computation of the vat holdback when holdback is defined
        (quantity * unit price * vat_rate * (holdback rate) )
        if holdback_on_vat is False
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_vat_with_holdback_on_vat(self):
        """
        Tests the computation of the vat holdback when holdback on vat is
        defined
        (quantity * unit price * vat_rate * (holdback rate) )
        if holdback_on_vat is True
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.637, ACCURACY))

    def test_get_holdback_vat_with_holdback_on_vat_and_no_vat(self):
        """
        Tests the computation of the vat holdback when holdback on vat is
        defined but no vat rate id defined
        (quantity * unit price * vat_rate * (holdback rate) )
        if holdback_on_vat is True
        """
        self.item.quantity = 5.0
        self.item.unit_price = 13.0
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_price_when_rounding(self):
        """
        Tests the computation of the price when rounding to ``ACCURACY`` is
        done.
        (quantity * unit price)
        """
        self.item.quantity = 5.00115
        self.item.unit_price = 13.0
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_price(),
                          round(65.0, ACCURACY))

    def test_get_vat_amount_when_rounding(self):
        """
        Tests the computation of the vat amount when rounding to ``ACCURACY``
        is done.
        (quantity * unit price * vat rate)
        """
        self.item.quantity = 5.00115
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6001
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_vat_amount(),
                          round(12.74, ACCURACY))

    def test_get_including_taxes_price_when_rounding(self):
        """
        Tests the computation of the including taxes price when rounding to
        ``ACCURACY`` is done.
        (quantity * unit price * (1.0 + vat rate) )
        """
        self.item.quantity = 5.00115
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6001
        self.item.holdback_rate = 5.0
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_including_taxes_price(),
                          round(77.74, ACCURACY))

    def test_get_holdback_when_rounding(self):
        """
        Tests the computation of the holdback when rounding to ``ACCURACY`` is
        done.
        (quantity * unit price * (holdback rate) )
        """
        self.item.quantity = 5.00115
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6
        self.item.holdback_rate = 5.004
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_amount(),
                          round(3.25, ACCURACY))

    def test_get_holdback_vat_when_rounding(self):
        """
        Tests the computation of the vat holdback when rounding to ``ACCURACY``
        is done.
        (quantity * unit price * vat_rate * (holdback rate) )
        if holdback_on_vat is True
        """
        self.item.quantity = 5.00115
        self.item.unit_price = 13.0
        self.item.vat_rate = 19.6001
        self.item.holdback_rate = 5.004
        self.item.holdback_on_vat = True
        self.assertEqual(self.item.get_holdback_vat_amount(),
                          round(0.637, ACCURACY))


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
