# -*- coding: utf-8 -*-

from pybill.lib.entities.accounting_docs import AccItem
from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress
import datetime

class FormatWriterGenericTest:
    """
    Abstract class containing various useful methods for testing accounting
    documents writing in XML.
    """
    def __init__(self) :
        if self.__class__ is AccDocXMLWriterGenericTest:
            raise NotImplementedError()

    def _fill_accdoc(self):
        """
        Method called after ``self.accdoc`` has been built in the ``setUp``
        method of the test cases. This method fills the accounting document
        with common content.
        """
        self.accdoc.doc_ref = u"A2"
        self.accdoc.place = u"A3"
        self.accdoc.date = u"A4"
        self.accdoc.date_num = datetime.date(2009, 10, 19)
        for i in range(5, 11, 2):
            self.accdoc.other_infos[u"A%d" % i] = u"A%d" % (i+1)
        self.accdoc.sender = self._build_address(u"B")
        self.accdoc.receiver = self._build_address(u"C")
        for i in range(1, 3):
            self.accdoc.remarks.append(u"D%d" % i)
        for key, num in [(u"E", 5), (u"F", 6), (u"G", 7), (u"H", 8)]:
            acc_item = AccItem()
            acc_item.quantity = (num * 100.0 + 1)
            acc_item.title = u"%s2" % key
            acc_item.unit_price = (num * 100.0 + 3)
            acc_item.vat_rate = (num * 100.0 + 4)
            self.accdoc.acc_items.append(acc_item)
        self.accdoc.acc_items[0].quantity_digits = 5
        self.accdoc.acc_items[0].details = [u"E3", u"E4"]
        self.accdoc.acc_items[0].unit_price = 505.0
        self.accdoc.acc_items[0].vat_rate = None
        self.accdoc.acc_items[1].unit_price_digits = 6
        self.accdoc.acc_items[2].holdback_rate = 7.0
        self.accdoc.acc_items[3].holdback_rate = 8.0
        self.accdoc.acc_items[3].holdback_on_vat = True

    def _build_address(self, prefix):
        """
        Builds a ``PersonAddress`` object suitable for the tests. The testing
        values in this object are prefixed with ``prefix``.
        """
        addr = PersonAddress()
        addr.honorific = u"%s1" % prefix
        addr.firstname = u"%s2" % prefix
        addr.other_name = u"%s3" % prefix
        addr.surname  = u"%s4" % prefix
        addr.lineage = u"%s5" % prefix
        self._fill_address(addr, prefix, 6)
        addr.organisation = org = OrganisationAddress()
        org.name = u"%s17" % prefix
        org.divisions = [u"%s18" % prefix, u"%s19" % prefix]
        org.job_titles = [u"%s20" % prefix, u"%s21" % prefix]
        self._fill_address(org, prefix, 22)
        return addr

    def _fill_address(self, addr, prefix, start_num):
        """
        Fills the ``address`` object with common pieces of information. The
        values of these pieces of information are prefixed with ``prefix`` and
        contain a number starting at ``start_num``.
        """
        addr.streets = [u"%s%d" % (prefix, start_num + 0),
                        u"%s%d" % (prefix, start_num + 1)]
        addr.post_box = u"%s%d" % (prefix, start_num + 2)
        addr.post_code = u"%s%d" % (prefix, start_num +3)
        addr.city = u"%s%d" % (prefix, start_num + 4)
        addr.state = u"%s%d" % (prefix, start_num + 5)
        addr.country = u"%s%d" % (prefix, start_num + 6)
        addr.phone = u"%s%d" % (prefix, start_num +7)
        addr.fax = u"%s%d" % (prefix, start_num + 8)
        addr.web = u"%s%d" % (prefix, start_num + 9)
        addr.email = u"%s%d" % (prefix, start_num + 10)
