# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs import Debit

from generic_test_accounting_docs import AbstractAccDocTest


class DebitTest(TestCase, AbstractAccDocTest):
    """
    Tests on the debit objects
    """
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.acc_doc = Debit("ID1")


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
