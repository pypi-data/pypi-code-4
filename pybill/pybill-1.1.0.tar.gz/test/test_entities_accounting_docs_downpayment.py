# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs import Downpayment

from generic_test_accounting_docs import AbstractAccDocTest


class DownpaymentTest(TestCase, AbstractAccDocTest):
    """
    Tests on the downpayment objects
    """
    def setUp(self):
        """
        Called before each test from this class
        """
        self.acc_doc = Downpayment("ID1")

    def test_empty_object(self):
        """
        Tests an empty downpayment: moreover the basic tests, tests the
        downpayment percent has the default value (30.0)
        """
        AbstractAccDocTest.test_empty_object(self)
        self.assertEqual(self.acc_doc.percent, 30.0)

    def test_get_total_without_holdback_to_be_paid(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(242.112, ACCURACY))

    def test_get_total_holdback_to_be_paid(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(28.812, ACCURACY))

    def test_get_total_to_be_paid(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(242.112, ACCURACY))

    def test_get_downpayment(self):
        """
        Tests the computation of the downpayment
        including taxes total * downpayment percent
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_downpayment(),
                          round(242.112, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_when_rounding(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(50.23, ACCURACY))

    def test_get_total_holdback_to_be_paid_when_rounding(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_when_rounding(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(8.232, ACCURACY))

    def test_get_total_to_be_paid_when_rounding(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(50.23, ACCURACY))

    def test_get_downpayment_when_rounding(self):
        """
        Tests the computation of the downpayment
        including taxes total * downpayment percent
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_downpayment(),
                          round(50.23, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. The
        total without holdback to be paid is actually equal to this total
        except if it is greater than the including taxes total minus the total
        of holdbacks. In this case, the total without holdback to
        be paid is limited to (including taxes total - total
        of holdbacks) and the remaining sum is in total of holdbacks to be
        paid.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(242.112, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. The
        total without holdback to be paid is actually equal to this total
        except if it is greater than the including taxes total minus the total
        of holdbacks. In this case, the total without holdback to
        be paid is limited to (including taxes total - total
        of holdbacks) and the remaining sum is in total of holdbacks to be
        paid.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_with_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(28.812, ACCURACY))

    def test_get_total_to_be_paid_with_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(242.112, ACCURACY))

    def test_get_downpayment_with_holdback(self):
        """
        Tests the computation of the downpayment when holdbacks are defined
        on some items
        including taxes total * downpayment percent
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_downpayment(),
                          round(242.112, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_huge_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. The
        total without holdback to be paid is actually equal to this total
        except if it is greater than the including taxes total minus the total
        of holdbacks. In this case, the total without holdback to
        be paid is limited to (including taxes total - total
        of holdbacks) and the remaining sum is in total of holdbacks to be
        paid.

        Here, we have a huge holdback and thus we are in the second case.
        """
        self.build_standard_example(with_holdbacks=True)
        for i in [0,2,3]:
            self.acc_doc.acc_items[i].holdback_rate = 95.0
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(138.772, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_huge_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. The
        total without holdback to be paid is actually equal to this total
        except if it is greater than the including taxes total minus the total
        of holdbacks. In this case, the total without holdback to
        be paid is limited to (including taxes total - total
        of holdbacks) and the remaining sum is in total of holdbacks to be
        paid.

        Here, we have a huge holdback and thus we are in the second case.
        """
        self.build_standard_example(with_holdbacks=True)
        for i in [0,2,3]:
            self.acc_doc.acc_items[i].holdback_rate = 95.0
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(103.340, ACCURACY))

    def test_get_total_vat_to_be_paid_with_huge_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example(with_holdbacks=True)
        for i in [0,2,3]:
            self.acc_doc.acc_items[i].holdback_rate = 95.0
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(28.812, ACCURACY))

    def test_get_total_to_be_paid_with_huge_holdback(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent.
        """
        self.build_standard_example(with_holdbacks=True)
        for i in [0,2,3]:
            self.acc_doc.acc_items[i].holdback_rate = 95.0
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(242.112, ACCURACY))

    def test_get_downpayment_with_huge_holdback(self):
        """
        Tests the computation of the downpayment when holdbacks are defined
        on some items
        including taxes total * downpayment percent
        """
        self.build_standard_example(with_holdbacks=True)
        for i in [0,2,3]:
            self.acc_doc.acc_items[i].holdback_rate = 95.0
        self.assertEqual(self.acc_doc.get_downpayment(),
                          round(242.112, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_different_percent(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. In this
        test, the downpayment percent is different from its default value
        """
        self.build_standard_example()
        self.acc_doc.percent = 50.0
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(403.52, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_different_percent(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. In this
        test, the downpayment percent is different from its default value
        """
        self.build_standard_example()
        self.acc_doc.percent = 50.0
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_with_different_percent(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. In this
        test, the downpayment percent is different from its default value
        """
        self.build_standard_example()
        self.acc_doc.percent = 50.0
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(48.020, ACCURACY))

    def test_get_total_to_be_paid_with_different_percent(self):
        """
        In the specific case of a downpayment, the total to be paid is the
        including taxes total mutiplied with the downpayment percent. In this
        test, the downpayment percent is different from its default value
        """
        self.build_standard_example()
        self.acc_doc.percent = 50.0
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(403.52, ACCURACY))

    def test_get_downpayment_with_different_percent(self):
        """
        Tests the computation of the downpayment with a downpayment percent
        different from its default value.
        including taxes total * downpayment percent
        """
        self.build_standard_example()
        self.acc_doc.percent = 50.0
        self.assertEqual(self.acc_doc.get_downpayment(),
                          round(403.52, ACCURACY))


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
