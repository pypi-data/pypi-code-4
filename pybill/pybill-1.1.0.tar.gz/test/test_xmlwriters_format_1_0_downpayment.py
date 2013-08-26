# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from lxml import etree
from pybill.lib.entities.accounting_docs import Downpayment

from pybill.lib.xmlwriters.accdoc_format_1_0 import write_accdoc_1_0_xml

from generic_test_formatwriter import FormatWriterGenericTest


EXPECTED = u"""<pbd:accounting-document xmlns:pbd="http://www.logilab.org/2010/PyBillDocument" pbd:format-version="PBD-1.0" pbd:type="downpayment">
  <pbd:downpayment-percent>1.7</pbd:downpayment-percent>
  <pbd:metadata>
    <pbd:id>A1</pbd:id>
    <pbd:doc-ref>A2</pbd:doc-ref>
    <pbd:place>A3</pbd:place>
    <pbd:date pbd:num="2009-10-19">A4</pbd:date>
    <pbd:info pbd:name="A5">A6</pbd:info>
    <pbd:info pbd:name="A7">A8</pbd:info>
    <pbd:info pbd:name="A9">A10</pbd:info>
  </pbd:metadata>
  <pbd:address pbd:role="from">
    <pbd:honorific>B1</pbd:honorific>
    <pbd:firstname>B2</pbd:firstname>
    <pbd:othername>B3</pbd:othername>
    <pbd:surname>B4</pbd:surname>
    <pbd:lineage>B5</pbd:lineage>
    <pbd:street>B6</pbd:street>
    <pbd:street>B7</pbd:street>
    <pbd:pob>B8</pbd:pob>
    <pbd:postcode>B9</pbd:postcode>
    <pbd:city>B10</pbd:city>
    <pbd:state>B11</pbd:state>
    <pbd:country>B12</pbd:country>
    <pbd:phone>B13</pbd:phone>
    <pbd:fax>B14</pbd:fax>
    <pbd:web>B15</pbd:web>
    <pbd:email>B16</pbd:email>
    <pbd:affiliation>
      <pbd:orgname>B17</pbd:orgname>
      <pbd:orgdiv>B18</pbd:orgdiv>
      <pbd:orgdiv>B19</pbd:orgdiv>
      <pbd:jobtitle>B20</pbd:jobtitle>
      <pbd:jobtitle>B21</pbd:jobtitle>
      <pbd:address>
        <pbd:street>B22</pbd:street>
        <pbd:street>B23</pbd:street>
        <pbd:pob>B24</pbd:pob>
        <pbd:postcode>B25</pbd:postcode>
        <pbd:city>B26</pbd:city>
        <pbd:state>B27</pbd:state>
        <pbd:country>B28</pbd:country>
        <pbd:phone>B29</pbd:phone>
        <pbd:fax>B30</pbd:fax>
        <pbd:web>B31</pbd:web>
        <pbd:email>B32</pbd:email>
      </pbd:address>
    </pbd:affiliation>
  </pbd:address>
  <pbd:address pbd:role="to">
    <pbd:honorific>C1</pbd:honorific>
    <pbd:firstname>C2</pbd:firstname>
    <pbd:othername>C3</pbd:othername>
    <pbd:surname>C4</pbd:surname>
    <pbd:lineage>C5</pbd:lineage>
    <pbd:street>C6</pbd:street>
    <pbd:street>C7</pbd:street>
    <pbd:pob>C8</pbd:pob>
    <pbd:postcode>C9</pbd:postcode>
    <pbd:city>C10</pbd:city>
    <pbd:state>C11</pbd:state>
    <pbd:country>C12</pbd:country>
    <pbd:phone>C13</pbd:phone>
    <pbd:fax>C14</pbd:fax>
    <pbd:web>C15</pbd:web>
    <pbd:email>C16</pbd:email>
    <pbd:affiliation>
      <pbd:orgname>C17</pbd:orgname>
      <pbd:orgdiv>C18</pbd:orgdiv>
      <pbd:orgdiv>C19</pbd:orgdiv>
      <pbd:jobtitle>C20</pbd:jobtitle>
      <pbd:jobtitle>C21</pbd:jobtitle>
      <pbd:address>
        <pbd:street>C22</pbd:street>
        <pbd:street>C23</pbd:street>
        <pbd:pob>C24</pbd:pob>
        <pbd:postcode>C25</pbd:postcode>
        <pbd:city>C26</pbd:city>
        <pbd:state>C27</pbd:state>
        <pbd:country>C28</pbd:country>
        <pbd:phone>C29</pbd:phone>
        <pbd:fax>C30</pbd:fax>
        <pbd:web>C31</pbd:web>
        <pbd:email>C32</pbd:email>
      </pbd:address>
    </pbd:affiliation>
  </pbd:address>
  <pbd:remark>D1</pbd:remark>
  <pbd:remark>D2</pbd:remark>
  <pbd:items-list>
    <pbd:item>
      <pbd:qty pbd:digits="5">501.0</pbd:qty>
      <pbd:description>
        <pbd:title>E2</pbd:title>
        <pbd:detail>E3</pbd:detail>
        <pbd:detail>E4</pbd:detail>
      </pbd:description>
      <pbd:unit-price pbd:digits="2">505.0</pbd:unit-price>
    </pbd:item>
    <pbd:item>
      <pbd:qty pbd:digits="0">601.0</pbd:qty>
      <pbd:description>
        <pbd:title>F2</pbd:title>
      </pbd:description>
      <pbd:unit-price pbd:digits="6">603.0</pbd:unit-price>
      <pbd:vat-rate>604.0</pbd:vat-rate>
    </pbd:item>
    <pbd:item pbd:holdback-rate="7.0" pbd:holdback-on-vat="no">
      <pbd:qty pbd:digits="0">701.0</pbd:qty>
      <pbd:description>
        <pbd:title>G2</pbd:title>
      </pbd:description>
      <pbd:unit-price pbd:digits="2">703.0</pbd:unit-price>
      <pbd:vat-rate>704.0</pbd:vat-rate>
    </pbd:item>
    <pbd:item pbd:holdback-rate="8.0" pbd:holdback-on-vat="yes">
      <pbd:qty pbd:digits="0">801.0</pbd:qty>
      <pbd:description>
        <pbd:title>H2</pbd:title>
      </pbd:description>
      <pbd:unit-price pbd:digits="2">803.0</pbd:unit-price>
      <pbd:vat-rate>804.0</pbd:vat-rate>
    </pbd:item>
  </pbd:items-list>
  <pbd:payment-terms>M1</pbd:payment-terms>
</pbd:accounting-document>
"""

class AccDocFormat10WriterDownpaymentTest(TestCase, FormatWriterGenericTest):
    def setUp(self):
        """
        Called before each test of this class.
        """
        self.accdoc = Downpayment(u"A1")
        self._fill_accdoc()
        self.accdoc.percent = 1.7
        self.accdoc.payment_terms = "M1"

    def test_write_xml_accdoc(self):
        xml_elt = write_accdoc_1_0_xml(self.accdoc)
        self.assertMultiLineEqual(etree.tostring(xml_elt, pretty_print=True),
                              EXPECTED)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
