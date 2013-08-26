# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.entities.accounting_docs import ClaimForm

from generic_test_accounting_docs import AbstractAccDocTest


class ClaimFormTest(TestCase, AbstractAccDocTest):
    """
    Tests on the claim form objects
    """
    def setUp(self):
        """
        Called before each test from this class
        """
        self.acc_doc = ClaimForm("ID1")


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
