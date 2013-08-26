# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from StringIO import StringIO

from pybill.lib.config.entities import ConfigData

from pybill.lib.config.xmlwriters import save_config
from pybill.lib.errors import PyBillWritingException


EXPECTED = u"""<?xml version="1.0" encoding="UTF-8"?>

<pbc:config xmlns:pbc="http://www.logilab.org/2010/PyBillConfig" pbc:format-version="PBC-1.0" pbc:name="Z0">
  <pbc:company>
    <pbc:logo-file>A1</pbc:logo-file>
    <pbc:orgname>A2</pbc:orgname>
    <pbc:address>
      <pbc:street>A3</pbc:street>
      <pbc:street>A4</pbc:street>
      <pbc:pob>A5</pbc:pob>
      <pbc:postcode>A6</pbc:postcode>
      <pbc:city>A7</pbc:city>
      <pbc:state>A8</pbc:state>
      <pbc:country>A9</pbc:country>
      <pbc:phone>A10</pbc:phone>
      <pbc:fax>A11</pbc:fax>
      <pbc:web>A12</pbc:web>
      <pbc:email>A13</pbc:email>
    </pbc:address>
  </pbc:company>
  <pbc:bank-data>
    <pbc:line>B1</pbc:line>
    <pbc:line>B2</pbc:line>
  </pbc:bank-data>
  <pbc:footer>
    <pbc:line>D1</pbc:line>
    <pbc:line>D2</pbc:line>
  </pbc:footer>
  <pbc:agreement-intro>
    <pbc:line>C1</pbc:line>
    <pbc:line>C2</pbc:line>
  </pbc:agreement-intro>
  <pbc:number-separators>
    <pbc:sign>F1</pbc:sign>
    <pbc:thousands>F2</pbc:thousands>
    <pbc:digits>F3</pbc:digits>
  </pbc:number-separators>
  <pbc:localisation>
    <pbc:colon>E0</pbc:colon>
    <pbc:phone-kw>E1</pbc:phone-kw>
    <pbc:fax-kw>E2</pbc:fax-kw>
    <pbc:web-kw>E3</pbc:web-kw>
    <pbc:email-kw>E4</pbc:email-kw>
    <pbc:doc-ref-kw>E5</pbc:doc-ref-kw>
    <pbc:receiver-kw>E9</pbc:receiver-kw>
    <pbc:sender-kw>E10</pbc:sender-kw>
    <pbc:on-date>E11</pbc:on-date>
    <pbc:bill>E12</pbc:bill>
    <pbc:claim-form>E13</pbc:claim-form>
    <pbc:downpayment>E14</pbc:downpayment>
    <pbc:debit>E16</pbc:debit>
    <pbc:pro-forma>E15</pbc:pro-forma>
    <pbc:number>E17</pbc:number>
    <pbc:dated>E18</pbc:dated>
    <pbc:valid-until>E19</pbc:valid-until>
    <pbc:intro-detail>E20</pbc:intro-detail>
    <pbc:quantity>E21</pbc:quantity>
    <pbc:description>E22</pbc:description>
    <pbc:vat-rate>E23</pbc:vat-rate>
    <pbc:unit-price>E24</pbc:unit-price>
    <pbc:tf-unit-price>E25</pbc:tf-unit-price>
    <pbc:price>E26</pbc:price>
    <pbc:tf-price>E27</pbc:tf-price>
    <pbc:it-price>E28</pbc:it-price>
    <pbc:holdback-on>E29</pbc:holdback-on>
    <pbc:ita-est>E30</pbc:ita-est>
    <pbc:total>E31</pbc:total>
    <pbc:tf-total>E32</pbc:tf-total>
    <pbc:vat-amount>E33</pbc:vat-amount>
    <pbc:it-total>E34</pbc:it-total>
    <pbc:including>E35</pbc:including>
    <pbc:holdback>E36</pbc:holdback>
    <pbc:on-tf>E37</pbc:on-tf>
    <pbc:on-vat>E38</pbc:on-vat>
    <pbc:debit-total>E39</pbc:debit-total>
    <pbc:charged-downpayment>E40</pbc:charged-downpayment>
    <pbc:charged-on>E41</pbc:charged-on>
    <pbc:issued-debit>E42</pbc:issued-debit>
    <pbc:issued-on>E43</pbc:issued-on>
    <pbc:to-be-paid>E44</pbc:to-be-paid>
    <pbc:payment-terms>E45</pbc:payment-terms>
    <pbc:to-bring-forward>E46</pbc:to-bring-forward>
    <pbc:carry-forward>E47</pbc:carry-forward>
    <pbc:your-ref-kw>E101</pbc:your-ref-kw>
    <pbc:purch-ref-kw>E102</pbc:purch-ref-kw>
    <pbc:supplier-ref-kw>E103</pbc:supplier-ref-kw>
  </pbc:localisation>
</pbc:config>
"""

LOCAL_DICT = { u'colon'              : u"E0",
               u'phone-kw'           : u"E1",
               u'fax-kw'             : u"E2",
               u'web-kw'             : u"E3",
               u'email-kw'           : u"E4",
               u'doc-ref-kw'         : u"E5",
               u'receiver-kw'        : u"E9",
               u'sender-kw'          : u"E10",
               u'on-date'            : u"E11",
               u'bill'               : u"E12",
               u'claim-form'         : u"E13",
               u'downpayment'        : u"E14",
               u'pro-forma'          : u"E15",
               u'debit'              : u"E16",
               u'number'             : u"E17",
               u'dated'              : u"E18",
               u'valid-until'        : u"E19",
               u'intro-detail'       : u"E20",
               u'quantity'           : u"E21",
               u'description'        : u"E22",
               u'vat-rate'           : u"E23",
               u'unit-price'         : u"E24",
               u'tf-unit-price'      : u"E25",
               u'price'              : u"E26",
               u'tf-price'           : u"E27",
               u'it-price'           : u"E28",
               u'holdback-on'        : u"E29",
               u'ita-est'            : u"E30",
               u'total'              : u"E31",
               u'tf-total'           : u"E32",
               u'vat-amount'         : u"E33",
               u'it-total'           : u"E34",
               u'including'          : u"E35",
               u'holdback'           : u"E36",
               u'on-tf'              : u"E37",
               u'on-vat'             : u"E38",
               u'debit-total'        : u"E39",
               u'charged-downpayment': u"E40",
               u'charged-on'         : u"E41",
               u'issued-debit'       : u"E42",
               u'issued-on'          : u"E43",
               u'to-be-paid'         : u"E44",
               u'payment-terms'      : u"E45",
               u'to-bring-forward'   : u"E46",
               u'carry-forward'      : u"E47",
               u'your-ref-kw'        : u"E101",
               u'purch-ref-kw'       : u"E102",
               u'supplier-ref-kw'    : u"E103",
             }


class ConfigXMLWriterTest(TestCase):
    def setUp(self):
        """
        Called before each test of this class. Builds a config object.
        """
        self.cfg = ConfigData()
        self.cfg.reference = u"Test"
        self.cfg.name = u"Z0"
        self.cfg.company_logo = u"A1"
        self.cfg.company_address.name = u"A2"
        self.cfg.company_address.streets = [u"A3", u"A4"]
        self.cfg.company_address.post_box = u"A5"
        self.cfg.company_address.post_code = u"A6"
        self.cfg.company_address.city = u"A7"
        self.cfg.company_address.state = u"A8"
        self.cfg.company_address.country = u"A9"
        self.cfg.company_address.phone = u"A10"
        self.cfg.company_address.fax = u"A11"
        self.cfg.company_address.web = u"A12"
        self.cfg.company_address.email = u"A13"
        self.cfg.bank_data_lines = [u"B1", u"B2"]
        self.cfg.agreement_intro_lines = [u"C1", u"C2"]
        self.cfg.footer_lines = [u"D1", u"D2"]
        self.cfg.number_separators = {u"sign": u"F1",
                                      u"thousands": u"F2",
                                      u"digits": u"F3"}
        self.cfg.local_phrases = LOCAL_DICT

    def test_write_data(self):
        """
        Tests the XMLConfigReader writes correctly an XML config file
        """
        # uses the XML parser sympathy to pass it a string stream instead of a
        # filename
        xml_result = StringIO()
        save_config(self.cfg, xml_result)
        self.assertMultiLineEqual(xml_result.getvalue(), EXPECTED)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
