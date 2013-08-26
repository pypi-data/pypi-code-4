# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from lxml import etree
import datetime
from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress
from pybill.lib.errors import PyBillReadingException

from pybill.lib.xmlreaders.utils import (AccDocFormatAbstractReader,
                                         read_person_address,
                                         read_text_from_xml_elt)


class FakeAccDocFormatReader(AccDocFormatAbstractReader):
    """
    Class used for testing the methods of the ``AccDocFormatAbstractReader``
    abstract class.
    """
    pass


class UtilFunctionsTest(TestCase):

    def test_read_text_from_simple_xml_element(self):
        """
        Tests the reading of a text inside an XML element.
        """
        xml_data = """
<root>
  <elt>TEXT</elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt")
        self.assertEqual(text, u"TEXT")

    def test_read_text_from_multiple_xml_element(self):
        """
        Tests the reading of a text inside an XML element when there are
        several XML elements (should only read the text in the first element).
        """
        xml_data = """
<root>
  <elt>TEXT1</elt>
  <elt>TEXT2</elt>
  <elt>TEXT3</elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt")
        self.assertEqual(text, u"TEXT1")
        
    def test_read_text_from_empty_xml_element(self):
        """
        Tests the reading of a text inside an empty XML element.
        """
        xml_data = """
<root>
  <elt></elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt")
        self.assertEqual(text, u"")

    def test_read_text_from_empty_xml_element_with_default_value(self):
        """
        Tests the reading of a text inside an empty XML element when a default
        value is defined.
        """
        xml_data = """
<root>
  <elt></elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt", u"FALLBACK")
        self.assertEqual(text, u"")

    def test_read_text_from_absent_xml_element(self):
        """
        Tests the reading of a text inside an XML element that doesn't exist.
        """
        xml_data = """
<root>
  <other-elt>TEXT</other-elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt")
        self.assertEqual(text, u"")

    def test_read_text_from_absent_xml_element_with_default_value(self):
        """
        Tests the reading of a text inside an XML element that doesn't exist 
        when a default value is defined.
        """
        xml_data = """
<root>
  <other-elt>TEXT</other-elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, u"elt", u"FALLBACK")
        self.assertEqual(text, u"FALLBACK")

    def test_read_text_from_complex_xml_element(self):
        """
        Tests the reading of a text inside an XML element with namespaces and
        several levels.
        """
        xml_data = """
<root xmlns:ns0="http://my.namespace.org/">
  <elt>
    <ns0:elt>TEXT</ns0:elt>
  </elt>
</root>
"""
        xml_root = etree.fromstring(xml_data)
        text = read_text_from_xml_elt(xml_root, 
                                      u"elt/{http://my.namespace.org/}elt")
        self.assertEqual(text, u"TEXT")

    def test_complete_address_reading(self):
        """
        Tests the reading of an address that has all of its fields filled.
        """
        xml_data = """
<address>
  <honorific>A1</honorific>
  <firstname>A2</firstname>
  <othername>A3</othername>
  <surname>A4</surname>
  <lineage>A5</lineage>
  <street>A6</street>
  <street>A7</street>
  <pob>A8</pob>
  <postcode>A9</postcode>
  <city>A10</city>
  <state>A11</state>
  <country>A12</country>
  <phone>A13</phone>
  <fax>A14</fax>
  <web>A15</web>
  <email>A16</email>
  <affiliation>
    <jobtitle>A17</jobtitle>
    <jobtitle>A18</jobtitle>
    <orgname>A19</orgname>
    <orgdiv>A20</orgdiv>
    <orgdiv>A21</orgdiv>
    <address>
      <street>A22</street>
      <street>A23</street>
      <pob>A24</pob>
      <postcode>A25</postcode>
      <city>A26</city>
      <state>A27</state>
      <country>A28</country>
      <phone>A29</phone>
      <fax>A30</fax>
      <web>A31</web>
      <email>A32</email>
    </address>
  </affiliation>
</address>
        """
        xml_addr = etree.fromstring(xml_data)
        addr = read_person_address(xml_addr)
        self.assertEqual(addr.__class__, PersonAddress)
        self.assertEqual(addr.honorific, u"A1")
        self.assertEqual(addr.firstname, u"A2")
        self.assertEqual(addr.other_name, u"A3")
        self.assertEqual(addr.surname, u"A4")
        self.assertEqual(addr.lineage, u"A5")
        self.assertEqual(addr.streets, [u"A6", u"A7"])
        self.assertEqual(addr.post_box, u"A8")
        self.assertEqual(addr.post_code, u"A9")
        self.assertEqual(addr.city, u"A10")
        self.assertEqual(addr.state, u"A11")
        self.assertEqual(addr.country, u"A12")
        self.assertEqual(addr.phone, u"A13")
        self.assertEqual(addr.fax, u"A14")
        self.assertEqual(addr.web, u"A15")
        self.assertEqual(addr.email, u"A16")
        # affiliation
        self.assertEqual(addr.organisation.__class__, OrganisationAddress)
        self.assertEqual(addr.organisation.job_titles, [u"A17", u"A18"])
        self.assertEqual(addr.organisation.name, u"A19")
        self.assertEqual(addr.organisation.divisions, [u"A20", u"A21"])
        self.assertEqual(addr.organisation.streets, [u"A22", u"A23"])
        self.assertEqual(addr.organisation.post_box, u"A24")
        self.assertEqual(addr.organisation.post_code, u"A25")
        self.assertEqual(addr.organisation.city, u"A26")
        self.assertEqual(addr.organisation.state, u"A27")
        self.assertEqual(addr.organisation.country, u"A28")
        self.assertEqual(addr.organisation.phone, u"A29")
        self.assertEqual(addr.organisation.fax, u"A30")
        self.assertEqual(addr.organisation.web, u"A31")
        self.assertEqual(addr.organisation.email, u"A32")

    def test_no_affiliation_address_reading(self):
        """
        Tests the reading of an address with no affiliation and thus no
        organisation address embedded
        """
        xml_data = """
<address>
  <honorific>A1</honorific>
  <firstname>A2</firstname>
  <othername>A3</othername>
  <surname>A4</surname>
  <lineage>A5</lineage>
  <street>A6</street>
  <street>A7</street>
  <pob>A8</pob>
  <postcode>A9</postcode>
  <city>A10</city>
  <state>A11</state>
  <country>A12</country>
  <phone>A13</phone>
  <fax>A14</fax>
  <web>A15</web>
  <email>A16</email>
</address>
        """
        xml_addr = etree.fromstring(xml_data)
        addr = read_person_address(xml_addr)
        self.assertEqual(addr.__class__, PersonAddress)
        self.assertEqual(addr.honorific, u"A1")
        self.assertEqual(addr.firstname, u"A2")
        self.assertEqual(addr.other_name, u"A3")
        self.assertEqual(addr.surname, u"A4")
        self.assertEqual(addr.lineage, u"A5")
        self.assertEqual(addr.streets, [u"A6", u"A7"])
        self.assertEqual(addr.post_box, u"A8")
        self.assertEqual(addr.post_code, u"A9")
        self.assertEqual(addr.city, u"A10")
        self.assertEqual(addr.state, u"A11")
        self.assertEqual(addr.country, u"A12")
        self.assertEqual(addr.phone, u"A13")
        self.assertEqual(addr.fax, u"A14")
        self.assertEqual(addr.web, u"A15")
        self.assertEqual(addr.email, u"A16")
        # affiliation
        self.assertEqual(addr.organisation, None)

    def test_regular_address_reading(self):
        """
        Tests the reading of a common address (with few fields).
        """
        xml_data = """
<address>
  <honorific>A1</honorific>
  <firstname>A2</firstname>
  <othername/>
  <surname>A3</surname>
  <phone>A4</phone>
  <email>A5</email>
  <affiliation>
    <jobtitle>A6</jobtitle>
    <orgname>A7</orgname>
    <address>
      <street>A8</street>
      <postcode>A9</postcode>
      <city>A10</city>
    </address>
  </affiliation>
</address>
        """
        xml_addr = etree.fromstring(xml_data)
        addr = read_person_address(xml_addr)
        self.assertEqual(addr.__class__, PersonAddress)
        self.assertEqual(addr.honorific, u"A1")
        self.assertEqual(addr.firstname, u"A2")
        self.assertEqual(addr.other_name, u"")
        self.assertEqual(addr.surname, u"A3")
        self.assertEqual(addr.phone, u"A4")
        self.assertEqual(addr.email, u"A5")
        # affiliation
        self.assertEqual(addr.organisation.__class__, OrganisationAddress)
        self.assertEqual(addr.organisation.job_titles, [u"A6"])
        self.assertEqual(addr.organisation.name, u"A7")
        self.assertEqual(addr.organisation.streets, [u"A8"])
        self.assertEqual(addr.organisation.post_code, u"A9")
        self.assertEqual(addr.organisation.city, u"A10")

    def test_address_with_namespace_reading(self):
        """
        Tests the reading of an address that uses a namespace.
        """
        xml_data = """
<address xmlns="http://www.logilab.org/TEST">
  <honorific>A1</honorific>
  <firstname>A2</firstname>
  <othername>A3</othername>
  <surname>A4</surname>
  <lineage>A5</lineage>
  <street>A6</street>
  <street>A7</street>
  <pob>A8</pob>
  <postcode>A9</postcode>
  <city>A10</city>
  <state>A11</state>
  <country>A12</country>
  <phone>A13</phone>
  <fax>A14</fax>
  <web>A15</web>
  <email>A16</email>
  <affiliation>
    <jobtitle>A17</jobtitle>
    <jobtitle>A18</jobtitle>
    <orgname>A19</orgname>
    <orgdiv>A20</orgdiv>
    <orgdiv>A21</orgdiv>
    <address>
      <street>A22</street>
      <street>A23</street>
      <pob>A24</pob>
      <postcode>A25</postcode>
      <city>A26</city>
      <state>A27</state>
      <country>A28</country>
      <phone>A29</phone>
      <fax>A30</fax>
      <web>A31</web>
      <email>A32</email>
    </address>
  </affiliation>
</address>
        """
        xml_addr = etree.fromstring(xml_data)
        addr = read_person_address(xml_addr,
                                   xml_ns="http://www.logilab.org/TEST")
        self.assertEqual(addr.__class__, PersonAddress)
        self.assertEqual(addr.honorific, u"A1")
        self.assertEqual(addr.firstname, u"A2")
        self.assertEqual(addr.other_name, u"A3")
        self.assertEqual(addr.surname, u"A4")
        self.assertEqual(addr.lineage, u"A5")
        self.assertEqual(addr.streets, [u"A6", u"A7"])
        self.assertEqual(addr.post_box, u"A8")
        self.assertEqual(addr.post_code, u"A9")
        self.assertEqual(addr.city, u"A10")
        self.assertEqual(addr.state, u"A11")
        self.assertEqual(addr.country, u"A12")
        self.assertEqual(addr.phone, u"A13")
        self.assertEqual(addr.fax, u"A14")
        self.assertEqual(addr.web, u"A15")
        self.assertEqual(addr.email, u"A16")
        # affiliation
        self.assertEqual(addr.organisation.__class__, OrganisationAddress)
        self.assertEqual(addr.organisation.job_titles, [u"A17", u"A18"])
        self.assertEqual(addr.organisation.name, u"A19")
        self.assertEqual(addr.organisation.divisions, [u"A20", u"A21"])
        self.assertEqual(addr.organisation.streets, [u"A22", u"A23"])
        self.assertEqual(addr.organisation.post_box, u"A24")
        self.assertEqual(addr.organisation.post_code, u"A25")
        self.assertEqual(addr.organisation.city, u"A26")
        self.assertEqual(addr.organisation.state, u"A27")
        self.assertEqual(addr.organisation.country, u"A28")
        self.assertEqual(addr.organisation.phone, u"A29")
        self.assertEqual(addr.organisation.fax, u"A30")
        self.assertEqual(addr.organisation.web, u"A31")
        self.assertEqual(addr.organisation.email, u"A32")

    def test_address_with_manual_namespace_reading(self):
        """
        Tests the reading of an address (with few fields) that manually defines
        a namespace on some elements (only these elements should be read).
        """
        xml_data = """
<ns:address xmlns:ns="http://www.logilab.org/TEST">
  <ns:honorific>A1</ns:honorific>
  <firstname>A2</firstname>
  <ns:surname>A3</ns:surname>
  <ns:phone>A4</ns:phone>
  <ns:email>A5</ns:email>
  <ns:affiliation>
    <ns:jobtitle>A6</ns:jobtitle>
    <ns:orgname>A7</ns:orgname>
    <ns:address>
      <street>A8</street>
      <ns:postcode>A9</ns:postcode>
      <ns:city>A10</ns:city>
    </ns:address>
  </ns:affiliation>
</ns:address>
        """
        xml_addr = etree.fromstring(xml_data)
        addr = read_person_address(xml_addr,
                                   xml_ns="http://www.logilab.org/TEST")
        self.assertEqual(addr.__class__, PersonAddress)
        self.assertEqual(addr.honorific, u"A1")
        self.assertEqual(addr.firstname, u"")
        self.assertEqual(addr.surname, u"A3")
        self.assertEqual(addr.phone, u"A4")
        self.assertEqual(addr.email, u"A5")
        # affiliation
        self.assertEqual(addr.organisation.__class__, OrganisationAddress)
        self.assertEqual(addr.organisation.job_titles, [u"A6"])
        self.assertEqual(addr.organisation.name, u"A7")
        self.assertEqual(addr.organisation.streets, [])
        self.assertEqual(addr.organisation.post_code, u"A9")
        self.assertEqual(addr.organisation.city, u"A10")


class AccDocFormatReaderCommonTest(TestCase):
    def setUp(self):
        """
        Called before each test of this class.
        """
        self.reader = FakeAccDocFormatReader()
        self.reader.filename = u"fake.xml"
        
    def test_xpath_selection(self):
        """
        Tests the selection of XML nodes with XPath pointers.
        """
        xml_data = """
<root>
  <elt num="i">az</elt>
  <elt num="ii">12</elt>
  <elt num="iii">2010-05-13</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        slct = self.reader._select_from_xpaths(xml, [u"elt"])
        self.assertEqual(len(slct), 3)
        for i in range(3):
            self.assertEqual(slct[i], xml[i])

    def test_xpath_complex_selection(self):
        """
        Tests the selection of XML nodes with XPath pointers.
        """
        xml_data = """
<root>
  <elt num="i">az</elt>
  <elt num="ii">12</elt>
  <elt num="iii">2010-05-13</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        slct = self.reader._select_from_xpaths(xml, [u"elt/@*|elt/text()"])
        self.assertEqual(slct,
                          [u"i", u"az", u"ii", u"12", u"iii", u"2010-05-13"])

    def test_xpath_selection_with_several_xpaths(self):
        """
        Tests the selection of XML nodes with XPath pointers (the first one
        doesn't select anything).
        """
        xml_data = """
<root>
  <elt num="i">az</elt>
  <elt num="ii">12</elt>
  <elt num="iii">2010-05-13</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        slct = self.reader._select_from_xpaths(xml,
                                      [u"nothing", u"elt/text()", u"elt/@num"])
        self.assertEqual(slct, ["az", "12", "2010-05-13"])

    def test_xpath_selection_with_namespace(self):
        """
        Tests the selection of XML nodes with XPath pointers containing the
        PyBill XML namespace.
        """
        xml_data = """
<root xmlns:ns="http://www.logilab.org/2010/PyBillDocument">
  <ns:elt num="i">az</ns:elt>
  <elt num="ii">12</elt>
  <ns:elt num="iii">2010-05-13</ns:elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        slct = self.reader._select_from_xpaths(xml, [u"pbd:elt/text()"])
        self.assertEqual(slct, ["az", "2010-05-13"])

    def test_xpath_typical_selection_with_namespace(self):
        """
        Tests the selection of XML nodes as it will be typically used.
        """
        xml_data = """
<ns:root xmlns:ns="http://www.logilab.org/2010/PyBillDocument">
  <ns:elt num="i">az</ns:elt>
  <ns:elt num="ii">12</ns:elt>
  <ns:elt num="iii">2010-05-13</ns:elt>
</ns:root>
        """
        xml = etree.fromstring(xml_data)
        slct = self.reader._select_from_xpaths(xml, [u"pbd:elt/@pbd:num",
                                                     u"pbd:elt/@num"])
        self.assertEqual(slct, ["i", "ii", "iii"])

    def test_xpath_reading_of_float_number(self):
        """
        Tests the reading of a float value with an XPath pointer.
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>012.700</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml, [u"elt[2]/text()"],
                                                   float)
        self.assertEqual(type(val), float)
        self.assertEqual(val, 12.7)

    def test_xpath_reading_of_integer_number(self):
        """
        Tests the reading of an integer value with an XPath pointer.
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>0012</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml, [u"elt[2]/text()"],
                                                   int)
        self.assertEqual(type(val), int)
        self.assertEqual(val, 12)

    def test_xpath_reading_of_integer_converted_to_float(self):
        """
        Tests the reading of an integer as a float with an XPath pointer.
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>0012</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml, [u"elt[2]/text()"],
                                                   float)
        self.assertEqual(type(val), float)
        self.assertEqual(val, 12.0)

    def test_xpath_reading_of_absent_number(self):
        """
        Tests the reading of an absent value with an XPath pointer.
        """
        xml_data = """
<root>
  <elt>az</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml, [u"elt[2]/text()"],
                                                   float)
        self.assertEqual(val, None)

    def test_use_default_value_when_xpath_reading_of_absent_number(self):
        """
        Tests the use of the default value when reading an absent value with
        an XPath pointer.
        """
        xml_data = """
<root>
  <elt>az</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml, [u"elt[2]/text()"],
                                                   float, 13.4)
        self.assertEqual(val, 13.4)

    def test_xpath_reading_when_impossible_conversion_to_float(self):
        """
        Tests the reading, with an XPath pointer, of a value that can't be
        converted to float (the reading should raise an exception).
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>12,7</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        self.assertRaises(PyBillReadingException,
                          self.reader._read_number_from_xpaths,
                          xml, [u"elt[2]/text()"], float)

    def test_xpath_reading_when_impossible_conversion_to_int(self):
        """
        Tests the reading, with an XPath pointer, of a value that can't be
        converted to integer (the reading should raise an exception).
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>12.0</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        self.assertRaises(PyBillReadingException,
                          self.reader._read_number_from_xpaths,
                          xml, [u"elt[2]/text()"], int)

    def test_xpath_reading_of_number_with_several_xpaths(self):
        """
        Tests the reading of a number with several XPath pointers (the first
        one doesn't point to anything).
        """
        xml_data = """
<root>
  <elt>az</elt>
  <elt>2</elt>
  <elt>12</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        val = self.reader._read_number_from_xpaths(xml,
                                                   [u"number/text()",
                                                    u"elt[3]/text()",
                                                    u"elt[2]/text()"],
                                                   float)
        self.assertEqual(type(val), float)
        self.assertEqual(val, 12.0)

    def test_xpath_reading_of_date(self):
        """
        Tests the reading, with an XPath pointer, of a date.
        """
        xml_data = """
<root>
  <elt>2009-10-20</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        date = self.reader._read_date_from_xpaths(xml, [u"elt/text()"])
        self.assertEqual(date, datetime.date(2009, 10, 20))

    def test_xpath_reading_of_normalized_date(self):
        """
        Tests the reading, with an XPath pointer, of a date that is in
        normalized format.
        """
        xml_data = """
<root>
  <elt>2009-10-20Z</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        date = self.reader._read_date_from_xpaths(xml, [u"elt/text()"])
        self.assertEqual(date, datetime.date(2009, 10, 20))

    def test_xpath_reading_of_local_date(self):
        """
        Tests the reading, with an XPath pointer, of a date that is locally
        expressed.
        """
        xml_data = """
<root>
  <elt>2009-10-20-05:00</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        date = self.reader._read_date_from_xpaths(xml, [u"elt/text()"])
        self.assertEqual(date, datetime.date(2009, 10, 20))

    def test_xpath_reading_of_date_when_wrong_format(self):
        """
        Tests the reading, with an XPath pointer, of a date that is wrongly
        written.
        """
        xml_data = """
<root>
  <elt>2009-10-2</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        self.assertRaises(PyBillReadingException,
                          self.reader._read_date_from_xpaths, xml,
                          [u"elt/text()"])

    def test_xpath_reading_of_date_when_bad_value(self):
        """
        Tests the reading, with an XPath pointer, of a date that contains a
        wrong value for the month.
        """
        xml_data = """
<root>
  <elt>2009-20-10</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        self.assertRaises(PyBillReadingException,
                          self.reader._read_date_from_xpaths, xml,
                          [u"elt/text()"])

    def test_xpath_reading_of_date_with_several_xpaths(self):
        """
        Tests the reading of a date with several XPath pointers (the first
        one doesn't point to anything).
        """
        xml_data = """
<root>
  <elt>2010-05-13</elt>
  <elt>2010-05-12</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        date = self.reader._read_date_from_xpaths(xml,
                                                  [u"date/text()",
                                                   u"elt[2]/text()",
                                                   u"elt[1]/text()"])
        self.assertEqual(date, datetime.date(2010, 05, 12))

    def test_xpath_reading_of_text(self):
        """
        Tests the reading of a text with an XPath pointer.
        """
        xml_data = """
<root>
  <elt>abc</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        text = self.reader._read_text_from_xpaths(xml, [u"elt/text()"])
        self.assertEqual(type(text), unicode)
        self.assertEqual(text, u"abc")

    def test_xpath_reading_of_text_with_several_xpaths(self):
        """
        Tests the reading of a text with several XPath pointers (the first
        one doesn't point to anything).
        """
        xml_data = """
<root>
  <elt>13</elt>
  <elt>1</elt>
</root>
        """
        xml = etree.fromstring(xml_data)
        text = self.reader._read_text_from_xpaths(xml,
                                                  [u"text/text()",
                                                   u"elt[2]/text()",
                                                   u"elt[1]/text()"])
        self.assertEqual(type(text), unicode)
        self.assertEqual(text, u"1")

        
# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()

