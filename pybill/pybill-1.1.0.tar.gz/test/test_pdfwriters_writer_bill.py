# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.pdfwriters import PDFWriter
from pybill.lib.entities.accounting_docs import (Bill, PreviousAccountingDoc)

from generic_test_pdfwriter import PDFWriterGenericTest


class PDFWriterBillTest(TestCase, PDFWriterGenericTest):
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.writer = PDFWriter()
        self.acc_doc = Bill("identifier")
        self.acc_doc.cfg_data = self._build_config_data()        
        self._fill_acc_doc_metadata(self.acc_doc)
        self.acc_doc.sender = self._build_person_address(u"sd")
        self.acc_doc.receiver = self._build_person_address(u"rc")
        self.acc_doc.payment_terms = u"payment_terms"
        self.entity_name = "bill"

    def test_write_three_items_and_one_downpayment(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and one previously charged downpayment.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        dwp = PreviousAccountingDoc()
        dwp.total = 5.0
        dwp.accdoc_id = "bill_id1"
        dwp.accdoc_date = "bill_date1"
        self.acc_doc.charged_downpayments.append(dwp)
        self._run_pdf_test("%s_three_items_and_one_downpayment.pdf"
                           % self.entity_name)

    def test_write_three_items_and_two_downpayments(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and two previously charged downpayments.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        dwp = PreviousAccountingDoc()
        dwp.total = 5.0
        dwp.accdoc_id = "bill_id1"
        dwp.accdoc_date = "bill_date1"
        self.acc_doc.charged_downpayments.append(dwp)
        dwp = PreviousAccountingDoc()
        dwp.total = 7.0
        dwp.vat_amount = 1.0
        dwp.accdoc_id = "bill_id2"
        dwp.accdoc_date = "bill_date2"
        self.acc_doc.charged_downpayments.append(dwp)
        self._run_pdf_test("%s_three_items_and_two_downpayments.pdf"
                           % self.entity_name)

    def test_write_three_items_and_one_debit(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and one previously issued debit.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        dbt = PreviousAccountingDoc()
        dbt.total = 5.0
        dbt.accdoc_id = "debit_id1"
        dbt.accdoc_date = "debit_date1"
        self.acc_doc.issued_debits.append(dbt)
        self._run_pdf_test("%s_three_items_and_one_debit.pdf"
                           % self.entity_name)

    def test_write_three_items_and_two_debits(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and two previously issued debits.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        dbt = PreviousAccountingDoc()
        dbt.total = 5.0
        dbt.accdoc_id = "debit_id1"
        dbt.accdoc_date = "debit_date1"
        self.acc_doc.issued_debits.append(dbt)
        dbt = PreviousAccountingDoc()
        dbt.total = 7.0
        dbt.vat_amount = 1.0
        dbt.accdoc_id = "debit_id2"
        dbt.accdoc_date = "debit_date2"
        self.acc_doc.issued_debits.append(dbt)
        self._run_pdf_test("%s_three_items_and_two_debits.pdf"
                           % self.entity_name)

    def test_write_three_items_one_downpayment_and_one_debit(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items, one previously charged downpayment and one previously issued
        debit.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        dbt = PreviousAccountingDoc()
        dbt.total = 5.0
        dbt.vat_amount = 0.5
        dbt.accdoc_id = "debit_id1"
        dbt.accdoc_date = "debit_date1"
        self.acc_doc.issued_debits.append(dbt)
        dwp = PreviousAccountingDoc()
        dwp.total = 11.0
        dwp.vat_amount = 2.0
        dwp.accdoc_id = "bill_id1"
        dwp.accdoc_date = "bill_date1"
        self.acc_doc.charged_downpayments.append(dwp)
        self._run_pdf_test("%s_three_items_one_downpayment_and_one_debit.pdf"
                           % self.entity_name)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
