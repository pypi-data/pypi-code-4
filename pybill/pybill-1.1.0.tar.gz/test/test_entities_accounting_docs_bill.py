# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs import PreviousAccountingDoc
from pybill.lib.entities.accounting_docs import Bill

from generic_test_accounting_docs import AbstractAccDocTest


class BillTest(TestCase, AbstractAccDocTest):
    """
    Tests on the bill objects.
    """
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.acc_doc = Bill("ID1")

    def define_downpayments_in_example(self):
        dwp = PreviousAccountingDoc()
        dwp.total = 23.0
        dwp.vat_amount = 2.0
        self.acc_doc.charged_downpayments.append(dwp)
        dwp = PreviousAccountingDoc()
        dwp.total = 13.0
        dwp.vat_amount = 1.0
        self.acc_doc.charged_downpayments.append(dwp)

    def define_debits_in_example(self):
        dbt = PreviousAccountingDoc()
        dbt.total = 27.0
        dbt.vat_amount = 3.0
        self.acc_doc.issued_debits.append(dbt)
        dbt = PreviousAccountingDoc()
        dbt.total = 17.0
        dbt.vat_amount = 1.5
        self.acc_doc.issued_debits.append(dbt)
        
    def test_get_vat_amount_for_rate_with_downpayment(self):
        """
        Tests the method giving the VAT amount for a given VAT rate when the
        list of already charged downpayments is not empty.
        """
        self.build_vat_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(1.0),
                          round(2.56, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(11.0),
                          round(3.85, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(21.0),
                          round(7.35, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(0.0, ACCURACY))

    def test_get_price_total_with_downpayment(self):
        """
        Tests the computation of the tax free total when the
        list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(711.0, ACCURACY))

    def test_get_including_taxes_total_with_downpayment(self):
        """
        Tests the computation of the including taxes total when the
        list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(807.04, ACCURACY))

    def test_get_holdback_amount_with_downpayment(self):
        """
        Tests the computation of the amount of holdbacks when the list
        of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_vat_amount_with_downpayment(self):
        """
        Tests the computation of the amount of holdbacks on VAT when the list
        of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_downpayment(self):
        """
        Tests the computation of the total without holdback to be paid when
        the list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(771.04, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_downpayment(self):
        """
        Tests the computation of the total of holdbacks to be paid when the
        list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_with_downpayment(self):
        """
        Tests the computation of the total of VAT to be paid when the
        list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(93.04, ACCURACY))

    def test_get_total_to_be_paid_with_downpayment(self):
        """
        Tests the computation of the total to be paid when the
        list of already charged downpayments is not empty.
        """
        self.build_standard_example()
        self.define_downpayments_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(771.04, ACCURACY))

    def test_get_vat_amount_for_rate_with_debit(self):
        """
        Tests the method giving the VAT amount for a given VAT rate when the
        list of already issued debits is not empty.
        """
        self.build_vat_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(1.0),
                          round(2.56, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(11.0),
                          round(3.85, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(21.0),
                          round(7.35, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(0.0, ACCURACY))

    def test_get_price_total_with_debit(self):
        """
        Tests the computation of the tax free total when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(711.0, ACCURACY))

    def test_get_including_taxes_total_with_debit(self):
        """
        Tests the computation of the including taxes total when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(807.04, ACCURACY))

    def test_get_holdback_amount_with_debit(self):
        """
        Tests the computation of the amount of holdbacks when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_vat_amount_with_debit(self):
        """
        Tests the computation of the amount of holdbacks on vat when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_debit(self):
        """
        Tests the computation of the total without holdback to be paid when
        the list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(763.04, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_debit(self):
        """
        Tests the computation of the total of holdbacks to be paid when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid_with_debit(self):
        """
        Tests the computation of the total of VAT to be paid when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(91.54, ACCURACY))

    def test_get_total_to_be_paid_with_debit(self):
        """
        Tests the computation of the total to be paid when the
        list of already issued debits is not empty.
        """
        self.build_standard_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(763.04, ACCURACY))

    def test_get_holdback_amount_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the amount of holdbacks when there
        are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(33.80, ACCURACY))

    def test_get_holdback_vat_amount_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the amount of holdbacks on vat when there
        are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(1.372, ACCURACY))

    def test_get_total_without_hldbk_tbp_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the total without holdback to be paid when
        there are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(691.868, ACCURACY))

    def test_get_total_holdback_tbp_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the total of holdbacks to be paid when there
        are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(35.172, ACCURACY))

    def test_get_total_vat_to_be_paid_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the total of VAT to be paid when there
        are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(88.54, ACCURACY))

    def test_get_total_to_be_paid_with_downpayment_debit_holdback(self):
        """
        Tests the computation of the total to be paid when there
        are charged downpayment, issued debits and holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(727.04, ACCURACY))

    def test_get_holdback_amount_with_downpayment_debit_huge_holdback(self):
        """
        Tests the computation of the amount of holdbacks when there
        are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(703.89, ACCURACY))

    def test_get_holdback_vat_amount_with_downpayment_debit_huge_holdback(self):
        """
        Tests the computation of the amount of holdbacks on vat when there
        are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(33.957, ACCURACY))

    def test_get_total_without_hldbk_tbp_with_dwnpymt_dbt_huge_holdback(self):
        """
        Tests the computation of the total without holdback to be paid when
        there are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(0.0, ACCURACY))

    def test_get_total_holdback_tbp_with_downpayment_debit_huge_holdback(self):
        """
        Tests the computation of the total of holdbacks to be paid when there
        are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(727.04, ACCURACY))

    def test_get_total_vat_tbp_with_downpayment_debit_huge_holdback(self):
        """
        Tests the computation of the total of VAT to be paid when there
        are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(88.54, ACCURACY))

    def test_get_total_to_be_paid_with_downpayment_debit_huge_holdback(self):
        """
        Tests the computation of the total to be paid when there
        are charged downpayment, issued debits and huge holdbacks.
        """
        self.build_standard_example(with_holdbacks=True)
        for it in self.acc_doc.acc_items:
            it.holdback_rate = 99.0
        self.define_downpayments_in_example()
        self.define_debits_in_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(727.04, ACCURACY))


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
