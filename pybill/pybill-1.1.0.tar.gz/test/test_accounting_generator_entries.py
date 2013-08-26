# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

import datetime
from pybill.lib.entities.accounting_docs import (Bill, ClaimForm, Debit,
                                                 Downpayment, ProForma)
from pybill.lib.entities.accounting_docs.utils import (AccItem,
                                                       PreviousAccountingDoc)
from pybill.lib.config.entities import ConfigData
from pybill.lib.accounting.utils import (Entry, CLIENT, CLIENT_HOLDBACK,
                                         PRODUCT, VAT)
from pybill.lib.accounting.generator import EntriesGenerator


class EntriesGeneratorTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.generator = EntriesGenerator()
        self.acc_doc = None

    def test_empty_object(self):
        self.assertEqual(self.generator.entries, [])

    def test_reset(self):
        self.generator.entries = [
            Entry(datetime.date(2009, 11, 06), u"ENTRY 1"),
            Entry(datetime.date(2009, 11, 06), u"ENTRY 2"),
                                 ]
        self.generator.reset_entries()
        self.assertEqual(self.generator.entries, [])

    def test_entry_generation_for_bill_without_holdbacks_previous_docs(self):
        self.acc_doc = Bill("id1")
        self._fill_accounting_doc()
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Bill # id1",
                          {u"4111": [1139.18]},
                          {u"701": [1050.00], u"4451": [89.18]})

    def test_entry_generation_for_bill_without_holdbacks(self):
        self.acc_doc = Bill("id1")
        self._fill_accounting_doc()
        for i in range(2):
            pad = PreviousAccountingDoc()
            pad.total = 2.0 * (i+1)
            pad.vat_amount = 0.7 * i
            self.acc_doc.charged_downpayments.append(pad)
        for i in range(2):
            pad = PreviousAccountingDoc()
            pad.total = 3.0 * (i+1)
            pad.vat_amount = 0.5 * i
            self.acc_doc.issued_debits.append(pad)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Bill # id1",
                          {u"4111": [1124.18]},
                          {u"701": [1036.20], u"4451": [87.98]})

    def test_entry_generation_for_bill(self):
        self.acc_doc = Bill("id1")
        self._fill_accounting_doc(with_holdbacks=True)
        for i in range(2):
            pad = PreviousAccountingDoc()
            pad.total = 2.0 * (i+1)
            pad.vat_amount = 0.7 * i
            self.acc_doc.charged_downpayments.append(pad)
        for i in range(2):
            pad = PreviousAccountingDoc()
            pad.total = 3.0 * (i+1)
            pad.vat_amount = 0.5 * i
            self.acc_doc.issued_debits.append(pad)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Bill # id1",
                          {u"4111": [1072.06], u"4112": [52.12]},
                          {u"701": [1036.20], u"4451": [87.98]})

    def test_entry_generation_for_claimform_without_holdbacks(self):
        self.acc_doc = ClaimForm("id1")
        self._fill_accounting_doc()
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Claim Form # id1",
                          {u"4111": [1139.18]},
                          {u"701": [1050.00], u"4451": [89.18]})

    def test_entry_generation_for_claimform(self):
        self.acc_doc = ClaimForm("id1")
        self._fill_accounting_doc(with_holdbacks=True)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Claim Form # id1",
                          {u"4111": [1087.06], u"4112": [52.12]},
                          {u"701": [1050.00], u"4451": [89.18]})

    def test_entry_generation_for_debit_without_holdbacks(self):
        self.acc_doc = Debit("id1")
        self._fill_accounting_doc()
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Debit # id1",
                          {u"701": [1050.00], u"4451": [89.18]},
                          {u"4111": [1139.18]})

    def test_entry_generation_for_debit(self):
        self.acc_doc = Debit("id1")
        self._fill_accounting_doc(with_holdbacks=True)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Debit # id1",
                          {u"701": [1050.00], u"4451": [89.18]},
                          {u"4111": [1087.06], u"4112": [52.12]})

    def test_entry_generation_for_downpayment_without_holdbacks(self):
        self.acc_doc = Downpayment("id1")
        self._fill_accounting_doc()
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Downpayment # id1",
                          {u"4111": [341.75]},
                          {u"701": [315.00], u"4451": [26.75]})

    def test_entry_generation_for_downpayment(self):
        self.acc_doc = Downpayment("id1")
        self._fill_accounting_doc(with_holdbacks=True)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Downpayment # id1",
                          {u"4111": [341.75]},
                          {u"701": [315.00], u"4451": [26.75]})

    def test_entry_generation_for_downpayment_with_huge_percent(self):
        self.acc_doc = Downpayment("id1")
        self.acc_doc.percent = 98.0
        self._fill_accounting_doc(with_holdbacks=True)
        self.generator.generate_entry(self.acc_doc)
        self._check_entry(u"Downpayment # id1",
                          {u"4111": [1087.06], u"4112": [29.34]},
                          {u"701": [1029.00], u"4451": [87.40]})

    def test_entry_generation_for_proforma_without_holdbacks(self):
        self.acc_doc = ProForma()
        self._fill_accounting_doc()
        self.generator.generate_entry(self.acc_doc)
        self.assertEqual(len(self.generator.entries), 0)

    def test_entry_generation_for_proforma(self):
        self.acc_doc = ProForma()
        self._fill_accounting_doc(with_holdbacks=True)
        self.generator.generate_entry(self.acc_doc)
        self.assertEqual(len(self.generator.entries), 0)

    def _check_entry(self, label, exp_debits, exp_credits):
        """
        Checks the unique accounting entry in the generator list.
        ``exp_debits`` and ``exp_credits`` are the expected debits and credits
        of this entry.
        """
        self.assertEqual(len(self.generator.entries), 1)
        entry = self.generator.entries[0]
        self.assertEqual(entry.date, datetime.date(2009, 11, 06))
        self.assertEqual(entry.explanation, label)
        self.assertEqual(entry.debits, exp_debits)
        self.assertEqual(entry.credits, exp_credits)
        
    def _fill_accounting_doc(self, with_holdbacks=False):
        """
        Fills the accounting document (``self.acc_doc``) used for the tests
        with some data.
        """
        self.acc_doc.date_num = datetime.date(2009, 11, 06)
        self.acc_doc.account_numbers = {CLIENT: u"4111",
                                        CLIENT_HOLDBACK: u"4112",
                                        VAT: u"4451", PRODUCT: u"701"}
        for i in range(4):
            item = AccItem()
            item.quantity = 5.0*(i+1)
            item.unit_price = 7.0*(i+1)
            if i in [1,2]:
                item.vat_rate = 19.6
            if with_holdbacks and i in [1,2,3]:
                item.holdback_rate = 5.0
                if i == 1:
                    item.holdback_on_vat = True
            self.acc_doc.acc_items.append(item)
        cfg = ConfigData()
        cfg.local_phrases = {u"bill": u"Bill",
                             u"claim-form": u"Claim Form",
                             u"debit": u"Debit",
                             u"downpayment": u"Downpayment",
                             u"pro-forma": u"Pro-Forma",
                             u"number": u"#"}
        self.acc_doc.cfg_data = cfg


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
