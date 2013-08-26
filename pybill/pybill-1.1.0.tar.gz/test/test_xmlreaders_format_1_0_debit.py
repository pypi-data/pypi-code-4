# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from lxml import etree

from pybill.lib.xmlreaders.accdoc_format_1_0 import AccDocFormat_1_0_Reader
from pybill.lib.entities.accounting_docs import Debit
from pybill.lib.config.entities import ConfigData

from generic_test_formatreader import FormatReaderGenericTest

xml_data = """
<accounting-document type="debit"
                     format-version="PBD-1.0"
                     xmlns="http://www.logilab.org/2010/PyBillDocument">
  <metadata>
    <id>A1</id>
    <doc-ref>A2</doc-ref>
    <place>A3</place>
    <date num="2009-10-19">A4</date>
    <info name="A5">A6</info>
    <info name="A7">A8</info>
    <info name="A9">A10</info>
  </metadata>

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

<items-list>
 <item>
  <qty digits="5">501.0</qty>
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
  <unit-price digits="6">603.0</unit-price>
  <vat-rate>604.0</vat-rate>
 </item>
 <item holdback-rate="7.0">
  <qty>701.0</qty>
  <description>
   <title>G2</title>
  </description>
  <unit-price>703.0</unit-price>
  <vat-rate>704.0</vat-rate>
 </item>
 <item holdback-rate="8.0" holdback-on-vat="yes">
  <qty>801.0</qty>
  <description>
   <title>H2</title>
  </description>
  <unit-price>803.0</unit-price>
  <vat-rate>804.0</vat-rate>
 </item>
</items-list>

</accounting-document>
"""


class AccDocFormat10ReaderDebitTest(TestCase, FormatReaderGenericTest):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.cfg = ConfigData()
        self.reader = AccDocFormat_1_0_Reader()

    def test_load_data(self):
        """
        Tests the Format_1_0_Reader reads correctly an XML debit document.
        """
        xml_root = etree.fromstring(xml_data)
        acc_doc = self.reader.read_accounting_doc(xml_root,
                                                  filename="X0.xml",
                                                  cfg=self.cfg)
        self.assertEqual(acc_doc.__class__, Debit)
        self._check_doc_generic_content(acc_doc)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
