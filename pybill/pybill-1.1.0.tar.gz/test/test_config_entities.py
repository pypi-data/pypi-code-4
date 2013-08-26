# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.entities.addresses import OrganisationAddress
from pybill.lib.config.entities import ConfigData


class ConfigDataTest(TestCase):

    def test_instanciation(self):
        """
        Tests the instanciation of an empty object.
        """
        cfg = ConfigData()
        self.assertEqual(cfg.reference, None)
        self.assertEqual(cfg.name, u"")
        self.assertEqual(cfg.company_logo, u"")
        self.assertTrue(cfg.company_address.__class__ is OrganisationAddress)
        # Just tests that the object seems to be empty
        self.assertEqual(cfg.company_address.name, u"")
        self.assertEqual(cfg.footer_lines, [])
        self.assertEqual(cfg.bank_data_lines, [])
        self.assertEqual(cfg.agreement_intro_lines, [])
        self.assertEqual(cfg.number_separators, {})
        self.assertEqual(cfg.local_phrases, {})

    def test_get_local_with_existing_keyword(self):
        """
        Tests the ``get_local_phrase`` with an existing keyword.
        """
        cfg = ConfigData()
        cfg.local_phrases = {u"A1": u"B1", u"A2": u"B2", u"A3": u"B3"}
        self.assertEqual(cfg.get_local_phrase(u"A2"), u"B2")
        self.assertEqual(cfg.get_local_phrase(u"A3"), u"B3")

    def test_get_local_with_unknown_keyword(self):
        """
        Tests the ``get_local_phrase`` with a non-existing keyword.
        """
        cfg = ConfigData()
        cfg.local_phrases = {u"A1": u"B1", u"A2": u"B2", u"A3": u"B3"}
        self.assertEqual(cfg.get_local_phrase(u"A4"), u"## A4 ##")
        self.assertEqual(cfg.get_local_phrase(u"B1"), u"## B1 ##")


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()

