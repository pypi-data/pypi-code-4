# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from StringIO import StringIO

from pybill.lib import PBD_1_0, PBD_0_X
from pybill.lib.accounting import CLIENT, CLIENT_HOLDBACK, PRODUCT, VAT
from pybill.lib.xmlreaders import AccDocXMLReader
from pybill.lib.errors import PyBillReadingException
from pybill.lib.config.entities import ConfigData
from pybill.lib.config import ConfigRegister
from pybill.lib.entities.accounting_docs import Bill

xml_data_1_0 = u"""
<accounting-document type="bill"
                     format-version="PBD-1.0"
                     xmlns="http://www.logilab.org/2010/PyBillDocument">

%s

<metadata>
  <id>A1</id>
  <doc-ref>A2</doc-ref>
  <place>A3</place>
  <date>A4</date>
</metadata>

<address role="from">
  <firstname>B1</firstname>
  <surname>B2</surname>
  <phone>B3</phone>
  <email>B4</email>
</address>

<address role="to">
  <firstname>C1</firstname>
  <surname>C2</surname>
  <affiliation>
    <orgname>C3</orgname>
    <address>
      <street>C4</street>
      <postcode>C5</postcode>
      <city>C6</city>
    </address>
  </affiliation>
</address>

<items-list>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat-rate>45.0</vat-rate>
 </item>
 <item>
  <qty>51.0</qty>
  <description>
   <title>E2</title>
  </description>
  <unit-price>43.0</unit-price>
  <vat-rate>44.0</vat-rate>
 </item>
</items-list>

<payment-terms>F1</payment-terms>

</accounting-document>
"""


xml_data_1_0_manual_ns = u"""
<pbd:accounting-document type="bill"
                         format-version="PBD-1.0"
                         xmlns:pbd="http://www.logilab.org/2010/PyBillDocument">

%s

<pbd:metadata>
  <pbd:id>A1</pbd:id>
  <pbd:doc-ref>A2</pbd:doc-ref>
  <pbd:place>A3</pbd:place>
  <pbd:date>A4</pbd:date>
</pbd:metadata>

<pbd:address role="from">
  <pbd:firstname>B1</pbd:firstname>
  <pbd:surname>B2</pbd:surname>
  <pbd:phone>B3</pbd:phone>
  <pbd:email>B4</pbd:email>
</pbd:address>

<pbd:address role="to">
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
  <pbd:qty digits="3">41.0</pbd:qty>
  <pbd:description>
   <pbd:title>D2</pbd:title>
   <pbd:detail>D3</pbd:detail>
  </pbd:description>
  <pbd:unit-price digits="1">44.0</pbd:unit-price>
  <pbd:vat-rate>45.0</pbd:vat-rate>
 </pbd:item>
 <pbd:item holdback-rate="15.0" holdback-on-vat="yes">
  <pbd:qty>51.0</pbd:qty>
  <pbd:description>
   <pbd:title>E2</pbd:title>
  </pbd:description>
  <pbd:unit-price>43.0</pbd:unit-price>
  <pbd:vat-rate>44.0</pbd:vat-rate>
 </pbd:item>
</pbd:items-list>

<pbd:payment-terms>F1</pbd:payment-terms>

</pbd:accounting-document>
"""

xml_data_0_X = u"""
<bill id="A1"
      our-ref="A2"
      your-ref="A3"
      purch-ref="A4"
      place="A5" date="A6">

%s

<address role="from">
  <firstname>B1</firstname>
  <surname>B2</surname>
  <phone>B3</phone>
  <email>B4</email>
</address>

<address role="to">
  <firstname>C1</firstname>
  <surname>C2</surname>
  <affiliation>
    <orgname>C3</orgname>
    <address>
      <street>C4</street>
      <postcode>C5</postcode>
      <city>C6</city>
    </address>
  </affiliation>
</address>

<selling>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat>45.0</vat>
 </item>
 <item>
  <qty>51.0</qty>
  <description>
   <title>E2</title>
  </description>
  <unit-price>43.0</unit-price>
  <vat>44.0</vat>
 </item>
</selling>

<payment-terms>F1</payment-terms>

</bill>
"""

xml_data_1_0_short = u"""
<accounting-document type="bill"
                     format-version="PBD-1.0"
                     xmlns="http://www.logilab.org/2010/PyBillDocument">

%s

<metadata>
  <id>A1</id>
  <doc-ref>A2</doc-ref>
  <place>A3</place>
  <date>A4</date>
</metadata>

<address role="to">
  <firstname>C1</firstname>
  <surname>C2</surname>
  <street>C4</street>
  <postcode>C5</postcode>
  <city>C6</city>
</address>

<items-list>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat-rate>45.0</vat-rate>
 </item>
</items-list>

<payment-terms>F1</payment-terms>

</accounting-document>
"""

xml_data_0_X_short = u"""
<bill id="A1"
      our-ref="A2"
      your-ref="A3"
      purch-ref="A4"
      place="A5" date="A6">

%s

<address role="to">
  <firstname>C1</firstname>
  <surname>C2</surname>
  <street>C4</street>
  <postcode>C5</postcode>
  <city>C6</city>
</address>

<selling>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat>45.0</vat>
 </item>
</selling>

<payment-terms>F1</payment-terms>

</bill>
"""

xml_data_1_0_error = u"""
<accounting-document type="bill"
                     format-version="PBD-1.0"
                     xmlns="http://www.logilab.org/2010/PyBillDocument">

%s

<metadata>
  <id>A1</id>
  <doc-ref>A2</doc-ref>
  <place>A3</place>
  <date>A4</date>
</metadata>

<address role="from">
  <firstname>C1</firstname>
  <surname>C2</surname>
</address>

<items-list>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat-rate>45.0</vat-rate>
 </item>
</items-list>

<payment-terms>F1</payment-terms>

</accounting-document>
"""

xml_data_0_X_error = u"""
<bill id="A1"
      our-ref="A2"
      your-ref="A3"
      purch-ref="A4"
      place="A5" date="A6">

%s

<address role="from">
  <firstname>C1</firstname>
  <surname>C2</surname>
</address>

<selling>
 <item>
  <qty>41.0</qty>
  <description>
   <title>D2</title>
   <detail>D3</detail>
  </description>
  <unit-price>44.0</unit-price>
  <vat>45.0</vat>
 </item>
</selling>

<payment-terms>F1</payment-terms>

</bill>
"""

class AccDocXMLReaderTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        cfg_reg = ConfigRegister()
        self.cfg1 = ConfigData()
        self.cfg1.local_phrases = {u"your-ref-kw"    : u"X1",
                                   u"purch-ref-kw"   : u"X2",
                                   u"supplier-ref-kw": u"X3",
                                  }
        cfg_reg.configs[u"default"] = self.cfg1
        self.cfg2 = ConfigData()
        self.cfg2.local_phrases = {u"your-ref-kw"    : u"Y1",
                                   u"purch-ref-kw"   : u"Y2",
                                   u"supplier-ref-kw": u"Y3",
                                  }
        cfg_reg.configs[u"my-config"] = self.cfg2
        cfg_reg.configs[u"my/config.xml"] = self.cfg2
        self.cfg3 = ConfigData()
        self.cfg3.local_phrases = {u"your-ref-kw"    : u"Z1",
                                   u"purch-ref-kw"   : u"Z2",
                                   u"supplier-ref-kw": u"Z3",
                                  }
        cfg_reg.configs[u"another-config"] = self.cfg3
        self.reader = AccDocXMLReader(cfg_reg)

    def test_load_faulty_xml(self):
        """
        Tests the AccDocXMLReader raises an exception when trying to read
        a syntaxically incorrect XML file.
        """
        faulty_data = """
<accounting-document type="bill" format-version="PBD-1.0">
  <metadata>
</accounting-document>
                      """
        stream = StringIO(faulty_data)
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        self.assertRaises(PyBillReadingException,
                          self.reader.load_data, stream)

    def test_read_doc_with_no_config(self):
        """
        Tests the AccDocXMLReader reads an accounting document that doesn't
        specify the configuration to be used (so default will be used).
        """
        stream = StringIO(xml_data_0_X % u"")
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg1)
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"X1": u"A3", u"X2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_doc_with_config(self):
        """
        Tests the AccDocXMLReader reads an accounting document that specifies
        in a processing instruction the configuration to be used.
        """
        stream = StringIO(xml_data_0_X % u'<?pybill config="my-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg2)
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"Y1": u"A3", u"Y2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_doc_with_imposed_config(self):
        """
        Tests the AccDocXMLReader reads an accounting document with a
        configuration imposed from outside. Checks the internal specification
        of the configuration is not used.
        """
        stream = StringIO(xml_data_0_X % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream, config_ref=u"my/config.xml")
        self.assertEqual(acc_doc.cfg_data, self.cfg2)
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"Y1": u"A3", u"Y2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_doc_with_accounts_definition(self):
        """
        Tests the AccDocXMLReader reads an accounting document that specifies
        in a processing instruction the impacted accounting accounts.
        """
        stream = StringIO(xml_data_0_X
                          % (u'<?accounts client="CLI" client-holdback="HLB" '
                             u'product="PRD" vat="VAT"?>'))
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.account_numbers,
                          {CLIENT : u"CLI", CLIENT_HOLDBACK: u"HLB",
                           PRODUCT: u"PRD", VAT            : u"VAT"})
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"X1": u"A3", u"X2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_doc_with_accounts_definition_and_config(self):
        """
        Tests the AccDocXMLReader reads an accounting document that specifies
        in a processing instruction the impacted accounting accounts.
        """
        stream = StringIO(xml_data_0_X
                          % (u'<?pybill config="my-config"?>\n'
                             u'<?accounts client="CLI" product="PRD"?>'))
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.account_numbers,
                          {CLIENT: u"CLI", PRODUCT: u"PRD"})
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"Y1": u"A3", u"Y2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_format_1_0_doc(self):
        """
        Tests the AccDocXMLReader correctly reads an accounting document
        in format 1.0.
        """
        stream = StringIO(xml_data_1_0 % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg3)
        self.assertEqual(acc_doc.origin_format, PBD_1_0)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_format_1_0_doc_manual_namespace(self):
        """
        Tests the AccDocXMLReader correctly reads an accounting document
        in format 1.0 with the namespace manually defined on all the elements
        but none of the attributes.
        """
        stream = StringIO(xml_data_1_0_manual_ns
                          % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg3)
        self.assertEqual(acc_doc.origin_format, PBD_1_0)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[0].quantity_digits, 3)
        self.assertEqual(acc_doc.acc_items[0].unit_price_digits, 1)
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.acc_items[1].holdback_rate, 15.0)
        self.assertEqual(acc_doc.acc_items[1].holdback_on_vat, True)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_format_0_X_doc(self):
        """
        Tests the AccDocXMLReader correctly reads an accounting document
        in format 0.X.
        """
        stream = StringIO(xml_data_0_X % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg3)
        self.assertEqual(acc_doc.origin_format, PBD_0_X) 
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.other_infos, {u"Z1": u"A3", u"Z2": u"A4"})
        self.assertEqual(len(acc_doc.acc_items), 2)
        self.assertEqual(acc_doc.acc_items[0].title, u"D2")
        self.assertEqual(acc_doc.acc_items[1].unit_price, 43.0)
        self.assertEqual(acc_doc.payment_terms, u"F1")

    def test_read_unknown_format_doc(self):
        """
        Tests the AccDocXMLReader doesn't read an accounting document in an
        unknown format.
        """
        wrong_data = u"""<wrong><?pybill config="default"?></wrong>"""
        stream = StringIO(wrong_data)
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        self.assertRaises(PyBillReadingException,
                          self.reader.load_data, stream)

    def test_read_format_1_0_short_doc(self):
        """
        Tests the AccDocXMLReader correctly reads an accounting document
        in format 1.0 with no sender data.
        """
        stream = StringIO(xml_data_1_0_short 
                          % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg3)
        self.assertEqual(acc_doc.origin_format, PBD_1_0)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.sender, None)
        self.assertEqual(acc_doc.receiver.honorific, u"")
        self.assertEqual(acc_doc.receiver.firstname, u"C1")
        self.assertEqual(acc_doc.receiver.surname, u"C2")
        self.assertEqual(acc_doc.receiver.streets, [u"C4"])
        self.assertEqual(acc_doc.receiver.post_code, u"C5")
        self.assertEqual(acc_doc.receiver.city, u"C6")
        self.assertEqual(acc_doc.receiver.organisation, None)

    def test_read_format_0_X_short_doc(self):
        """
        Tests the AccDocXMLReader correctly reads an accounting document
        in format 0.X with no sender data.
        """
        stream = StringIO(xml_data_0_X_short 
                          % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        acc_doc = self.reader.load_data(stream)
        self.assertEqual(acc_doc.cfg_data, self.cfg3)
        self.assertEqual(acc_doc.origin_format, PBD_0_X)
        self.assertEqual(acc_doc.__class__, Bill)
        self.assertEqual(acc_doc.id, u"A1")
        self.assertEqual(acc_doc.sender, None)
        self.assertEqual(acc_doc.receiver.honorific, u"")
        self.assertEqual(acc_doc.receiver.firstname, u"C1")
        self.assertEqual(acc_doc.receiver.surname, u"C2")
        self.assertEqual(acc_doc.receiver.streets, [u"C4"])
        self.assertEqual(acc_doc.receiver.post_code, u"C5")
        self.assertEqual(acc_doc.receiver.city, u"C6")
        self.assertEqual(acc_doc.receiver.organisation, None)

    def test_read_format_1_0_error_doc(self):
        """
        Tests the AccDocXMLReader correctly raises an exception when reading
        an accounting document in format 1.0 with no receiver data.
        """
        stream = StringIO(xml_data_1_0_error
                          % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        self.assertRaises(PyBillReadingException, 
                          self.reader.load_data, stream)

    def test_read_format_0_X_error_doc(self):
        """
        Tests the AccDocXMLReader correctly raises an exception when reading
        an accounting document in format 0.X with no receiver data.
        """
        stream = StringIO(xml_data_0_X_error 
                          % u'<?pybill config="another-config"?>')
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        self.assertRaises(PyBillReadingException, 
                          self.reader.load_data, stream)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
