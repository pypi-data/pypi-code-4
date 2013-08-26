# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.pdfwriters import PDFWriter
from pybill.lib.entities.accounting_docs import Downpayment

from generic_test_pdfwriter import PDFWriterGenericTest


class PDFWriterDownpaymentTest(TestCase, PDFWriterGenericTest):
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.writer = PDFWriter()
        self.acc_doc = Downpayment("identifier")
        self.acc_doc.cfg_data = self._build_config_data()        
        self._fill_acc_doc_metadata(self.acc_doc)
        self.acc_doc.sender = self._build_person_address(u"sd")
        self.acc_doc.receiver = self._build_person_address(u"rc")
        self.acc_doc.payment_terms = "payment_terms"
        self.entity_name = "downpayment"

    def test_write_three_items_and_different_percent(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and a different downpayment percent.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.percent = 50.00444
        self._run_pdf_test("%s_three_items_and_different_percent.pdf"
                           % self.entity_name)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
