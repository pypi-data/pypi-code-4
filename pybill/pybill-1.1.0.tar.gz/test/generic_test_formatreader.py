# -*- coding: utf-8 -*-

from pybill.lib import ACCURACY, PBD_1_0, PBD_0_X
import datetime


class FormatReaderGenericTest:
    """
    Abstract class containing various useful methods for testing XML accounting
    documents reading.
    """
    def __init__(self):
        if self.__class__ is FormatReaderGenericTest:
            raise NotImplementedError()

    def _check_doc_generic_content(self, acc_doc, format=PBD_1_0,
                                   check_items=True, check_id=True):
        """
        Checks document generic attributes data (i.e. attributes common to all
        accounting documents
        
        :parameter acc_doc: Object whose content will be tested. This
                            object has been produced by an XML reader.
        :type acc_doc: GenericAccountingDoc
        
        :parameter format: Format of the data that has been read. The format
                           leads to different reading procedures (default
                           values, etc.) and thus different pieces of data. Can
                           be ``u"PBD-1.0"`` (default value) or ``u"PBD-0.X"``.
        :type format: unicode

        :parameter check_items: When set to True (default value), this method
                                will check the items in the ``acc_items`` list
                                of the accounting document object (``acc_doc``).
        :type check_items: bool

        :parameter check_id: When set to True (default value), this method
                             will check the value of the id of the accounting
                             document object (``acc_doc``).
        :type check_id: bool
        """
        # Checks document metadata
        if check_id:
            self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.origin_format, format)
        self.assertEqual(acc_doc.doc_ref, u"A2")
        self.assertEqual(acc_doc.place, u"A3")
        self.assertEqual(acc_doc.date, u"A4")
        if format == PBD_1_0:
            self.assertEqual(acc_doc.date_num, datetime.date(2009, 10, 19))
        self.assertEqual(acc_doc.other_infos, {u"A5": u"A6", u"A7": u"A8",
                                                u"A9": u"A10"})
        # Checks the addresses
        self._check_acc_doc_address(acc_doc.sender, u'B')
        self._check_acc_doc_address(acc_doc.receiver, u'C')
        # Checks remarks
        self.assertEqual(acc_doc.remarks, [u"D1", u"D2"])
        # Checks accounting items
        if check_items:
            self.assertEqual(len(acc_doc.acc_items), 4)
            if format == PBD_1_0:
                expected_cnt = [ (501.0, 5, u"E2", [u"E3", u"E4"], 505.0,
                                  ACCURACY, None, None, False),
                                 (601.0, 0, u"F2", [], 603.0, 6, 604.0,
                                  None, False),
                                 (701.0, 0, u"G2", [], 703.0, ACCURACY, 704.0,
                                  7.0, False),
                                 (801.0, 0, u"H2", [], 803.0, ACCURACY, 804.0,
                                  8.0, True),
                               ]
            elif format == PBD_0_X:
                expected_cnt = [ (501.0, 1, u"E2", [u"E3",u"E4"], 505.0,
                                  ACCURACY, 19.6, None, False),
                                 (601.0, 1, u"F2", [], 603.0, ACCURACY, 604.0,
                                  None, False),
                                 (701.0, 1, u"G2", [], 703.0, ACCURACY, 704.0,
                                  None, False),
                                 (801.0, 1, u"H2", [], 803.0, ACCURACY, 804.0,
                                  None, False),
                               ]
            else:
                # Unknown format
                expected_cnt = [ (None, None, None, None, None, None, None,
                                  None, None) ]*4
            for i in range(4):
                self._check_sold_item_with_content(acc_doc.acc_items[i],
                                                   expected_cnt[i])
        # Checks the config object (that is still not defined)
        self.assertEqual(acc_doc.cfg_data, None)

    def _check_acc_doc_address(self, addr, code):
        """
        Checks the address of the accounting document contains expected data

        :parameter code: either u"B" or u"C" (first letter of the address data
                         content)
        :parameter code: unicode
        """
        self.assertEqual(addr.honorific, u"%s1" % code)
        self.assertEqual(addr.firstname, u"%s2" % code)
        self.assertEqual(addr.other_name, u"%s3" % code)
        self.assertEqual(addr.surname, u"%s4" % code)
        self.assertEqual(addr.lineage, u"%s5" % code)
        self.assertEqual(addr.streets,[u"%s6" % code, u"%s7" % code])
        self.assertEqual(addr.post_box, u"%s8" % code)
        self.assertEqual(addr.post_code, u"%s9" % code)
        self.assertEqual(addr.city, u"%s10" % code)
        self.assertEqual(addr.state, u"%s11" % code)
        self.assertEqual(addr.country, u"%s12" % code)
        self.assertEqual(addr.phone, u"%s13" % code)
        self.assertEqual(addr.fax, u"%s14" % code)
        self.assertEqual(addr.web, u"%s15" % code)
        self.assertEqual(addr.email, u"%s16" % code)
        # affiliation
        self.assertEqual(addr.organisation.name, u"%s19" % code)
        self.assertEqual(addr.organisation.job_titles, [u"%s17" % code,
                                                         u"%s18" % code])
        self.assertEqual(addr.organisation.divisions, [u"%s20" % code,
                                                        u"%s21" % code])
        self.assertEqual(addr.organisation.streets, [u"%s22" % code,
                                                      u"%s23" % code])
        self.assertEqual(addr.organisation.post_box, u"%s24" % code)
        self.assertEqual(addr.organisation.post_code, u"%s25" % code)
        self.assertEqual(addr.organisation.city, u"%s26" % code)
        self.assertEqual(addr.organisation.state, u"%s27" % code)
        self.assertEqual(addr.organisation.country, u"%s28" % code)
        self.assertEqual(addr.organisation.phone, u"%s29" % code)
        self.assertEqual(addr.organisation.fax, u"%s30" % code)
        self.assertEqual(addr.organisation.web, u"%s31" % code)
        self.assertEqual(addr.organisation.email, u"%s32" % code)

    def _check_sold_item_with_content(self, acc_it, content):
        """
        Compares the AccItem 'acc_it' with the data contained in the tuple
        'content'.

        :parameter acc_it: Accounting item whose content is to be compared with
                           the expected content.
        :type acc_it: AccItem

        :parameter content: tuple containing the expected values for the
                            accounting object content. These values are:
                            (quantity, number of digits for the quantity,
                            title, list of details, unit price, number of
                            digits for the unit price, VAT rate,
                            holdback rate, boolean set when the holdback applies
                            on the VAT)
        :type content: (float, int, unicode, list, float, float, float, bool)
        """
        self.assertEqual(acc_it.quantity, content[0])
        self.assertEqual(acc_it.quantity_digits, content[1])
        self.assertEqual(acc_it.title, content[2])
        self.assertEqual(acc_it.details, content[3])
        self.assertEqual(acc_it.unit_price, content[4])
        self.assertEqual(acc_it.unit_price_digits, content[5])
        self.assertEqual(acc_it.vat_rate, content[6])
        self.assertEqual(acc_it.holdback_rate, content[7])
        self.assertEqual(acc_it.holdback_on_vat, content[8])
