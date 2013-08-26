# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from lxml import etree
from StringIO import StringIO
from tempfile import mkdtemp
from os import remove, listdir, rmdir
from os import path as osp

from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress
from pybill.lib.xmlwriters.utils import (build_address_xml_element,
                                         open_xml_outfile)


class AccDocFormatAddressWriterTest(TestCase):
    def test_complete_address_writing(self):
        """
        Tests the writing of an address that has all of its fields filled.
        """
        # Address building
        addr = PersonAddress()
        addr.honorific = u"A1"
        addr.firstname = u"A2"
        addr.other_name = u"A3"
        addr.surname = u"A4"
        addr.lineage = u"A5"
        addr.streets = [u"A6" , u"A7"]
        addr.post_box = u"A8"
        addr.post_code = u"A9"
        addr.city = u"A10"
        addr.state = u"A11"
        addr.country = u"A12"
        addr.phone = u"A13"
        addr.fax = u"A14"
        addr.web = u"A15"
        addr.email = u"A16"
        # affiliation
        addr.organisation = OrganisationAddress()
        addr.organisation.name = u"A17"
        addr.organisation.divisions = [u"A18", u"A19"]
        addr.organisation.job_titles = [u"A20", u"A21"]
        addr.organisation.streets = [u"A22", u"A23"]
        addr.organisation.post_box = u"A24"
        addr.organisation.post_code = u"A25"
        addr.organisation.city = u"A26"
        addr.organisation.state = u"A27"
        addr.organisation.country = u"A28"
        addr.organisation.phone = u"A29"
        addr.organisation.fax = u"A30"
        addr.organisation.web = u"A31"
        addr.organisation.email = u"A32"
        # Expected result (XML)
        expected_xml = u"""<address>
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
    <orgname>A17</orgname>
    <orgdiv>A18</orgdiv>
    <orgdiv>A19</orgdiv>
    <jobtitle>A20</jobtitle>
    <jobtitle>A21</jobtitle>
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
        xml_elt = build_address_xml_element(addr)
        self.assertMultiLineEqual(etree.tostring(xml_elt, pretty_print=True),
                              expected_xml)

    def test_no_affiliation_address_writing(self):
        """
        Tests the writing of an address with no organisation address embedded
        and thus no affiliation.
        """
        # Address building
        addr = PersonAddress()
        addr.honorific = u"A1"
        addr.firstname = u"A2"
        addr.other_name = u"A3"
        addr.surname = u"A4"
        addr.lineage = u"A5"
        addr.streets = [u"A6" , u"A7"]
        addr.post_box = u"A8"
        addr.post_code = u"A9"
        addr.city = u"A10"
        addr.state = u"A11"
        addr.country = u"A12"
        addr.phone = u"A13"
        addr.fax = u"A14"
        addr.web = u"A15"
        addr.email = u"A16"
        # Expected result (XML)
        expected_xml = u"""<address>
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
        xml_elt = build_address_xml_element(addr)
        self.assertMultiLineEqual(etree.tostring(xml_elt, pretty_print=True),
                              expected_xml)

    def test_regular_address_writing(self):
        """
        Tests the writing of a common address (with few fields).
        """
        # Address building
        addr = PersonAddress()
        addr.honorific = u"A1"
        addr.firstname = u"A2"
        addr.surname = u"A3"
        addr.phone = u"A4"
        addr.email = u"A5"
        # affiliation
        addr.organisation = OrganisationAddress()
        addr.organisation.name = u"A6"
        addr.organisation.job_titles = [u"A7"]
        addr.organisation.streets = [u"A8"]
        addr.organisation.post_code = u"A9"
        addr.organisation.city = u"A10"
        # Expected result (XML)
        expected_xml = """<address>
  <honorific>A1</honorific>
  <firstname>A2</firstname>
  <surname>A3</surname>
  <phone>A4</phone>
  <email>A5</email>
  <affiliation>
    <orgname>A6</orgname>
    <jobtitle>A7</jobtitle>
    <address>
      <street>A8</street>
      <postcode>A9</postcode>
      <city>A10</city>
    </address>
  </affiliation>
</address>
"""
        xml_elt = build_address_xml_element(addr)
        self.assertMultiLineEqual(etree.tostring(xml_elt, pretty_print=True),
                              expected_xml)

    def test_complete_address_writing_with_namespace(self):
        """
        Tests the writing of an address that has all of its fields filled and
        that must be written in a given XML namespace.
        """
        # Address building
        addr = PersonAddress()
        addr.honorific = u"A1"
        addr.firstname = u"A2"
        addr.other_name = u"A3"
        addr.surname = u"A4"
        addr.lineage = u"A5"
        addr.streets = [u"A6" , u"A7"]
        addr.post_box = u"A8"
        addr.post_code = u"A9"
        addr.city = u"A10"
        addr.state = u"A11"
        addr.country = u"A12"
        addr.phone = u"A13"
        addr.fax = u"A14"
        addr.web = u"A15"
        addr.email = u"A16"
        # affiliation
        addr.organisation = OrganisationAddress()
        addr.organisation.name = u"A17"
        addr.organisation.divisions = [u"A18", u"A19"]
        addr.organisation.job_titles = [u"A20", u"A21"]
        addr.organisation.streets = [u"A22", u"A23"]
        addr.organisation.post_box = u"A24"
        addr.organisation.post_code = u"A25"
        addr.organisation.city = u"A26"
        addr.organisation.state = u"A27"
        addr.organisation.country = u"A28"
        addr.organisation.phone = u"A29"
        addr.organisation.fax = u"A30"
        addr.organisation.web = u"A31"
        addr.organisation.email = u"A32"
        # Expected result (XML)
        expected_xml = u"""<ns0:address xmlns:ns0="http://www.logilab.org/TEST">
  <ns0:honorific>A1</ns0:honorific>
  <ns0:firstname>A2</ns0:firstname>
  <ns0:othername>A3</ns0:othername>
  <ns0:surname>A4</ns0:surname>
  <ns0:lineage>A5</ns0:lineage>
  <ns0:street>A6</ns0:street>
  <ns0:street>A7</ns0:street>
  <ns0:pob>A8</ns0:pob>
  <ns0:postcode>A9</ns0:postcode>
  <ns0:city>A10</ns0:city>
  <ns0:state>A11</ns0:state>
  <ns0:country>A12</ns0:country>
  <ns0:phone>A13</ns0:phone>
  <ns0:fax>A14</ns0:fax>
  <ns0:web>A15</ns0:web>
  <ns0:email>A16</ns0:email>
  <ns0:affiliation>
    <ns0:orgname>A17</ns0:orgname>
    <ns0:orgdiv>A18</ns0:orgdiv>
    <ns0:orgdiv>A19</ns0:orgdiv>
    <ns0:jobtitle>A20</ns0:jobtitle>
    <ns0:jobtitle>A21</ns0:jobtitle>
    <ns0:address>
      <ns0:street>A22</ns0:street>
      <ns0:street>A23</ns0:street>
      <ns0:pob>A24</ns0:pob>
      <ns0:postcode>A25</ns0:postcode>
      <ns0:city>A26</ns0:city>
      <ns0:state>A27</ns0:state>
      <ns0:country>A28</ns0:country>
      <ns0:phone>A29</ns0:phone>
      <ns0:fax>A30</ns0:fax>
      <ns0:web>A31</ns0:web>
      <ns0:email>A32</ns0:email>
    </ns0:address>
  </ns0:affiliation>
</ns0:address>
"""
        xml_elt = build_address_xml_element(addr,
                                          xml_ns="http://www.logilab.org/TEST")
        self.assertMultiLineEqual(etree.tostring(xml_elt, pretty_print=True),
                              expected_xml)

class XMLOpenTest(TestCase):
    """
    Tests the function that opens an XML file and writes the XML declaration.
    """
    def test_opening_from_filename(self):
        # Creates a temporary directory
        temp_dir = mkdtemp()
        # Runs the function
        filename = osp.join(temp_dir, "test.xml")
        out = open_xml_outfile(filename)
        out.close()
        # Tests the result
        res_file = open(filename)
        result = res_file.read()
        self.assertMultiLineEqual(result,
                              '<?xml version="1.0" encoding="UTF-8"?>\n\n')
        res_file.close()
        # Removes the temporary directory
        for fname in listdir(temp_dir):
            remove(osp.join(temp_dir, fname))
        rmdir(temp_dir)

    def test_opening_from_file(self):
        # Creates an opened file
        opened_file = StringIO()
        # Runs the function
        out = open_xml_outfile(opened_file)
        # Tests the result
        self.assertEqual(out, opened_file)
        self.assertMultiLineEqual(out.getvalue(),
                              '<?xml version="1.0" encoding="UTF-8"?>\n\n')

# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()

