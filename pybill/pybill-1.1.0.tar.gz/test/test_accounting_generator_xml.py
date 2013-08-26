# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

import datetime
from StringIO import StringIO
from pybill.lib.accounting.utils import Entry
from pybill.lib.accounting.generator import EntriesGenerator

EXPECTED_XML = """<?xml version="1.0" encoding="%s"?>

<ecritures>
  <ecriture date="2009-11-06">
    <libelle>ENTRY 1</libelle>
    <debit compte="4111" montant="56.0"/>
    <debit compte="4111" montant="23.45"/>
    <debit compte="4112" montant="12.34"/>
    <credit compte="4451" montant="11.79"/>
    <credit compte="701" montant="80.0"/>
  </ecriture>
  <ecriture date="2009-11-06">
    <libelle>ENTRY 2</libelle>
    <debit compte="4111" montant="123.0"/>
    <debit compte="4113" montant="45.6"/>
    <credit compte="4111" montant="77.59"/>
    <credit compte="701" montant="91.01"/>
  </ecriture>
</ecritures>
"""


class EntriesGeneratorTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        self.generator = EntriesGenerator()
        ent = Entry(datetime.date(2009, 11, 06), u"ENTRY 1")
        ent.debits = {u"4111": [56.00, 23.45], u"4112": [12.34]}
        ent.credits = {u"701": [80.00], u"4451": [11.79]}
        self.generator.entries.append(ent)
        ent = Entry(datetime.date(2009, 11, 06), u"ENTRY 2")
        ent.debits = {u"4111": [123.00], u"4113": [45.60]}
        ent.credits = {u"701": [91.01], u"4111": [77.59]}
        self.generator.entries.append(ent)

    def test_xml_writing(self):
        out = StringIO()
        self.generator.write_entries_in_xml(out)
        self.assertMultiLineEqual(out.getvalue(), EXPECTED_XML % "UTF-8")

    def test_xml_writing_other_encoding(self):
        out = StringIO()
        self.generator.write_entries_in_xml(out, encoding="ISO-8859-1")
        self.assertMultiLineEqual(out.getvalue(), EXPECTED_XML % "ISO-8859-1")

    def test_xml_writing_no_entry(self):
        out = StringIO()
        self.generator.reset_entries()
        self.generator.write_entries_in_xml(out)
        self.assertMultiLineEqual(out.getvalue(), "")


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
