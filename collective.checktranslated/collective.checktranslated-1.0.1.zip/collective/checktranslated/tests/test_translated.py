# -*- coding: UTF-8 -*-
import unittest2 as unittest

from collective.checktranslated.symptoms import check_translated
from collective.checktranslated.testing import CHECKTRANSLATED_INTEGRATION

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestTranslated(unittest.TestCase):
    site_languages = ['fr', 'en', 'nl']
    layer = CHECKTRANSLATED_INTEGRATION

    def test_not_translated_in_nl(self):
        site = self.layer['portal']
        setRoles(site, TEST_USER_ID, ('Manager',))
        site.invokeFactory(type_name="Folder", id="fr_object", language="fr")
        fr_object = site.fr_object
        self.site_languages = ['fr', 'nl']
        status, description = check_translated(fr_object, self.site_languages)
        self.assertFalse(status)
        self.assertTrue(description in u"There is no nl translation")

    def test_neutral(self):
        site = self.layer['portal']
        setRoles(site, TEST_USER_ID, ('Manager',))
        site.invokeFactory(type_name="Folder", id="neutral_object", language="")
        neutral_object = site.neutral_object
        status, description = check_translated(neutral_object, self.site_languages)
        self.assertFalse(status)
        self.assertEqual(description, u"This is a neutral language object.")

    def test_translated(self):
        site = self.layer['portal']
        setRoles(site, TEST_USER_ID, ('Manager',))
        site.invokeFactory(type_name="Document", id="fr", language="fr")
        fr = site.fr

        site.invokeFactory(type_name="Document", id="nl", language="nl")
        nl = site.nl
        fr.addTranslationReference(nl)

        self.site_languages = ['fr', 'nl']
        status, description = check_translated(fr, self.site_languages)
        self.assertTrue(status)
        self.assertEqual(description, u"Translated into all languages.")

        self.site_languages = ['fr', 'nl']
        status, description = check_translated(nl, self.site_languages)
        self.assertTrue(status)
        self.assertEqual(description, u"Translated into all languages.")

    def test_one_langue(self):
        site = self.layer['portal']
        setRoles(site, TEST_USER_ID, ('Manager',))
        site.invokeFactory(type_name="Folder", id="one_lang_site", language="fr")
        obj = site.one_lang_site
        status, description = check_translated(obj, ['fr'])
        self.assertFalse(status)
        self.assertEqual(description, u"There is only one language installed on your site.")

    def test_not_installed_lang(self):
        site = self.layer['portal']
        setRoles(site, TEST_USER_ID, ('Manager',))
        site.invokeFactory(type_name="Folder", id="not_installed_lang", language="de")
        obj = site.not_installed_lang
        status, description = check_translated(obj, ['nl', 'en'])
        self.assertFalse(status)
        self.assertEqual(description, u"Language not installed.")
