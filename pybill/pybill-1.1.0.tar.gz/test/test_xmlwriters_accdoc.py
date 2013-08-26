# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from StringIO import StringIO

from pybill.lib.config.entities import ConfigData
from pybill.lib.entities.accounting_docs import Bill, AccItem
from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress

from pybill.lib.xmlwriters import write_accounting_doc
from pybill.lib.errors import PyBillWritingException


EXPECTED_XML_1_0 = u"""<?xml version="1.0" encoding="%s"?>
%s
<pbd:accounting-document xmlns:pbd="http://www.logilab.org/2010/PyBillDocument" pbd:format-version="PBD-1.0" pbd:type="bill">
  <pbd:metadata>
    <pbd:id>A1</pbd:id>
    <pbd:doc-ref>A2</pbd:doc-ref>
    <pbd:place>A3</pbd:place>
    <pbd:date>A4</pbd:date>
  </pbd:metadata>
  <pbd:address pbd:role="from">
    <pbd:firstname>B1</pbd:firstname>
    <pbd:surname>B2</pbd:surname>
    <pbd:phone>B3</pbd:phone>
    <pbd:email>B4</pbd:email>
  </pbd:address>
  <pbd:address pbd:role="to">
    <pbd:firstname>C1</pbd:firstname>
    <pbd:surname>C2</pbd:surname>
    <pbd:affiliation>
      <pbd:orgname>C3</pbd:orgname>
      <pbd:address>
        <pbd:street>C4</pbd:street>
        <pbd:postcode>C5</pbd:postcode>
        <pbd:city>C6</pbd:city>
      </pbd:address>
    </pbd:affiliation>
  </pbd:address>
  <pbd:items-list>
    <pbd:item>
      <pbd:qty pbd:digits="0">41.0</pbd:qty>
      <pbd:description>
        <pbd:title>D2</pbd:title>
        <pbd:detail>D3</pbd:detail>
      </pbd:description>
      <pbd:unit-price pbd:digits="2">44.0</pbd:unit-price>
      <pbd:vat-rate>45.0</pbd:vat-rate>
    </pbd:item>
    <pbd:item>
      <pbd:qty pbd:digits="0">51.0</pbd:qty>
      <pbd:description>
        <pbd:title>E2</pbd:title>
      </pbd:description>
      <pbd:unit-price pbd:digits="2">53.0</pbd:unit-price>
      <pbd:vat-rate>54.0</pbd:vat-rate>
    </pbd:item>
  </pbd:items-list>
  <pbd:payment-terms>F1</pbd:payment-terms>
</pbd:accounting-document>
"""


class AccDocXMLWriterTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class. Builds the bill used in the
        tests.
        """
        self.accdoc = Bill(u"A1")
        self.accdoc.doc_ref = u"A2"
        self.accdoc.place = u"A3"
        self.accdoc.date = u"A4"
        self.accdoc.sender = PersonAddress()
        self.accdoc.sender.firstname = u"B1"
        self.accdoc.sender.surname = u"B2"
        self.accdoc.sender.phone = u"B3"
        self.accdoc.sender.email = u"B4"
        self.accdoc.receiver = PersonAddress()
        self.accdoc.receiver.firstname = u"C1"
        self.accdoc.receiver.surname = u"C2"
        self.accdoc.receiver.organisation = OrganisationAddress()
        self.accdoc.receiver.organisation.name = u"C3"
        self.accdoc.receiver.organisation.streets = [u"C4"]
        self.accdoc.receiver.organisation.post_code = u"C5"
        self.accdoc.receiver.organisation.city = u"C6"
        it1 = AccItem()
        it1.quantity = 41.0
        it1.title = u"D2"
        it1.details = [u"D3"]
        it1.unit_price = 44.0
        it1.vat_rate = 45.0
        self.accdoc.acc_items.append(it1)
        it2 = AccItem()
        it2.quantity = 51.0
        it2.title = u"E2"
        it2.unit_price = 53.0
        it2.vat_rate = 54.0
        self.accdoc.acc_items.append(it2)
        self.accdoc.payment_terms = u"F1"

    def test_write_doc_with_no_config(self):
        """
        Tests the writing of an accounting document that is not linked to
        a configuration object (even if this should never exist...)
        """
        xml_result = StringIO()
        # uses the writer sympathy to pass it a string stream instead of a
        # filename
        write_accounting_doc(self.accdoc, xml_result)
        self.assertMultiLineEqual(xml_result.getvalue(),
                              EXPECTED_XML_1_0 % (u"UTF-8", u""))

    def test_write_doc_with_config(self):
        """
        Tests the writing of an accounting document that is linked to
        a configuration object.
        """
        self.accdoc.cfg_data = ConfigData()
        self.accdoc.cfg_data.name = u"Test"
        xml_result = StringIO()
        # uses the writer sympathy to pass it a string stream instead of a
        # filename
        write_accounting_doc(self.accdoc, xml_result)
        self.assertMultiLineEqual(xml_result.getvalue(),
                EXPECTED_XML_1_0 % (u"UTF-8", u'\n<?pybill config="Test"?>\n'))

    def test_write_doc_with_config_and_encoding(self):
        """
        Tests the writing of an accounting document that is linked to
        a configuration object and that must be written in a different 
        encoding.
        """
        self.accdoc.cfg_data = ConfigData()
        self.accdoc.cfg_data.name = u"Test"
        xml_result = StringIO()
        # uses the writer sympathy to pass it a string stream instead of a
        # filename
        write_accounting_doc(self.accdoc, xml_result, encoding="ISO-8859-1")
        self.assertMultiLineEqual(xml_result.getvalue(),
           EXPECTED_XML_1_0 % (u"ISO-8859-1", u'\n<?pybill config="Test"?>\n'))

    def test_write_unknown_format(self):
        """
        Tests the writer doesn't write un unknown formats.
        """
        xml_result = StringIO()
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        self.assertRaises(PyBillWritingException, write_accounting_doc,
                          self.accdoc, xml_result, u"PDB-1.1")


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
