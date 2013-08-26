# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

import datetime
from pybill.lib.errors import PyBillProcessingException
from pybill.lib.accounting.utils import Entry


class EntryTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.entry = Entry(datetime.date(2009, 11, 06), u"EXPLANATION")

    def test_empty_object(self):
        self.assertEqual(self.entry.date, datetime.date(2009, 11, 06))
        self.assertEqual(self.entry.explanation, u"EXPLANATION")
        self.assertEqual(self.entry.debits,  {})
        self.assertEqual(self.entry.credits, {})

    def test_add_credit_movement(self):
        self.entry.add_movement(u"44", 11.0)
        self.assertEqual(self.entry.debits,  {})
        self.assertEqual(self.entry.credits, {u"44": [11.0]})

    def test_add_debit_movement(self):
        self.entry.add_movement(u"44", -11.0)
        self.assertEqual(self.entry.credits, {})
        self.assertEqual(self.entry.debits,  {u"44": [11.0]})

    def test_add_credit_movement_when_rounding(self):
        self.entry.add_movement(u"44", 11.145)
        self.assertEqual(self.entry.debits,  {})
        self.assertEqual(self.entry.credits, {u"44": [11.15]})

    def test_add_debit_movement_when_rounding(self):
        self.entry.add_movement(u"44", -11.145)
        self.assertEqual(self.entry.credits, {})
        self.assertEqual(self.entry.debits,  {u"44": [11.15]})

    def test_add_credit_debit_movements_on_same_account(self):
        self.entry.add_movement(u"44", 11.0)
        self.entry.add_movement(u"44", -9.0)
        self.assertEqual(self.entry.debits,  {u"44": [ 9.0]})
        self.assertEqual(self.entry.credits, {u"44": [11.0]})

    def test_add_credit_movements_on_same_account(self):
        self.entry.add_movement(u"44", 11.0)
        self.entry.add_movement(u"44", 13.0)
        self.assertEqual(self.entry.debits,  {})
        self.assertEqual(self.entry.credits, {u"44": [11.0, 13.0]})

    def test_add_credit_movements_on_two_accounts(self):
        self.entry.add_movement(u"44", 11.0)
        self.entry.add_movement(u"45",  9.0)
        self.assertEqual(self.entry.debits,  {})
        self.assertEqual(self.entry.credits, {u"44": [11.0], u"45": [9.0]})

    def test_add_debit_movements_on_same_account(self):
        self.entry.add_movement(u"44", -11.0)
        self.entry.add_movement(u"44", -13.0)
        self.assertEqual(self.entry.credits, {})
        self.assertEqual(self.entry.debits,  {u"44": [11.0, 13.0]})

    def test_add_debit_movements_on_two_accounts(self):
        self.entry.add_movement(u"44", -11.0)
        self.entry.add_movement(u"45",  -9.0)
        self.assertEqual(self.entry.credits, {})
        self.assertEqual(self.entry.debits,  {u"44": [11.0], u"45": [9.0]})

    def test_check_correct_entry(self):
        self.entry.debits = {u"44": [12.0, 3.0], u"45": [4.0]}
        self.entry.credits = {u"46": [19.0]}
        self.assertTrue(self.entry.check())

    def test_check_incorrect_entry(self):
        self.entry.debits = {u"44": [12.0, 1.0], u"45": [4.0]}
        self.entry.credits = {u"46": [19.0], u"47": [1.0]}
        self.assertRaises(PyBillProcessingException, self.entry.check)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
