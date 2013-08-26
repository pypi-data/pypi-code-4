# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from lxml import etree

from pybill.lib import PBD_0_X
from pybill.lib.xmlreaders.accdoc_format_0_X import AccDocFormat_0_X_Reader
from pybill.lib.entities.accounting_docs import ClaimForm
from pybill.lib.config.entities import ConfigData

from generic_test_formatreader import FormatReaderGenericTest

xml_data = """
<claim-form id="A1"
            our-ref="A2"
            your-ref="A6"
            purch-ref="A8"
            supplier-ref="A10"
            place="A3" date="A4">

<address role="from">
  <honorific>B1</honorific>
  <firstname>B2</firstname>
  <othername>B3</othername>
  <surname>B4</surname>
  <lineage>B5</lineage>
  <street>B6</street>
  <street>B7</street>
  <pob>B8</pob>
  <postcode>B9</postcode>
  <city>B10</city>
  <state>B11</state>
  <country>B12</country>
  <phone>B13</phone>
  <fax>B14</fax>
  <web>B15</web>
  <email>B16</email>
  <affiliation>
    <jobtitle>B17</jobtitle>
    <jobtitle>B18</jobtitle>
    <orgname>B19</orgname>
    <orgdiv>B20</orgdiv>
    <orgdiv>B21</orgdiv>
    <address>
      <street>B22</street>
      <street>B23</street>
      <pob>B24</pob>
      <postcode>B25</postcode>
      <city>B26</city>
      <state>B27</state>
      <country>B28</country>
      <phone>B29</phone>
      <fax>B30</fax>
      <web>B31</web>
      <email>B32</email>
    </address>
  </affiliation>
</address>

<address role="to">
  <honorific>C1</honorific>
  <firstname>C2</firstname>
  <othername>C3</othername>
  <surname>C4</surname>
  <lineage>C5</lineage>
  <street>C6</street>
  <street>C7</street>
  <pob>C8</pob>
  <postcode>C9</postcode>
  <city>C10</city>
  <state>C11</state>
  <country>C12</country>
  <phone>C13</phone>
  <fax>C14</fax>
  <web>C15</web>
  <email>C16</email>
  <affiliation>
    <jobtitle>C17</jobtitle>
    <jobtitle>C18</jobtitle>
    <orgname>C19</orgname>
    <orgdiv>C20</orgdiv>
    <orgdiv>C21</orgdiv>
    <address>
      <street>C22</street>
      <street>C23</street>
      <pob>C24</pob>
      <postcode>C25</postcode>
      <city>C26</city>
      <state>C27</state>
      <country>C28</country>
      <phone>C29</phone>
      <fax>C30</fax>
      <web>C31</web>
      <email>C32</email>
    </address>
  </affiliation>
</address>

<remark>D1</remark>
<remark>D2</remark>

<selling>
 <item>
  <qty>501.0</qty>
  <description>
   <title>E2</title>
   <detail>E3</detail>
   <detail>E4</detail>
  </description>
  <unit-price>505.0</unit-price>
 </item>
 <item>
  <qty>601.0</qty>
  <description>
   <title>F2</title>
  </description>
  <unit-price>603.0</unit-price>
  <vat>604.0</vat>
 </item>
 <item>
  <qty>701.0</qty>
  <description>
   <title>G2</title>
  </description>
  <unit-price>703.0</unit-price>
  <vat>704.0</vat>
 </item>
 <item>
  <qty>801.0</qty>
  <description>
   <title>H2</title>
  </description>
  <unit-price>803.0</unit-price>
  <vat>804.0</vat>
 </item></selling>

<payment-terms>I1</payment-terms>

</claim-form>
"""


class AccDocFormat0XReaderClaimFormTest(TestCase, FormatReaderGenericTest):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.cfg = ConfigData()
        self.cfg.local_phrases = {"your-ref-kw": "A5",
                                  "purch-ref-kw": "A7",
                                  "supplier-ref-kw": "A9",
                                 }
        self.reader = AccDocFormat_0_X_Reader()

    def test_load_data(self):
        """
        Tests the Format_0_X_Reader reads correctly an XML claim form document.
        """
        xml_root = etree.fromstring(xml_data)
        acc_doc = self.reader.read_accounting_doc(xml_root,
                                                  filename="X0.xml",
                                                  cfg=self.cfg)
        self.assertEqual(acc_doc.__class__, ClaimForm)
        self.assertEqual(acc_doc.payment_terms, "I1")
        self._check_doc_generic_content(acc_doc, format=PBD_0_X)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
