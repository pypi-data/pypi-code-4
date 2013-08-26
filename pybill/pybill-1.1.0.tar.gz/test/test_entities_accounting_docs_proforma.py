# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs import ProForma

from generic_test_accounting_docs import AbstractAccDocTest


class ProFormaTest(TestCase, AbstractAccDocTest):
    """
    Tests on the pro-forma objects.
    """
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.acc_doc = ProForma()

    def build_standard_example(self, with_holdbacks=False):
        """
        Creates a pro-forma document: a basic accounting document with a
        validity date.

        :parameter with_holdbacks: When set to ``True``, holdbacks are
                                   inserted in the items.
        :type with_holdbacks: bool
        """
        AbstractAccDocTest.build_standard_example(self,
                                                 with_holdbacks=with_holdbacks)
        self.acc_doc.validity_date = u"30/06/2009"

    def test_get_total_without_holdback_to_be_paid(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(0.0, ACCURACY))

    def test_get_total_holdback_to_be_paid(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(0.0, ACCURACY))

    def test_get_total_to_be_paid(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(0.0, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_when_rounding(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(0.0, ACCURACY))

    def test_get_total_holdback_to_be_paid_when_rounding(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_when_rounding(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(0.0, ACCURACY))

    def test_get_total_to_be_paid_when_rounding(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(0.0, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_holdback(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(0.0, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_holdback(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_with_holdback(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(0.0, ACCURACY))

    def test_get_total_to_be_paid_with_holdback(self):
        """
        In the specific case of a pro-forma, nothing must be paid by the client
        (it's not realy a bill). Thus, the ``get_total_*_to_be_paid()``
        methods always return 0.0.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(0.0, ACCURACY))


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
