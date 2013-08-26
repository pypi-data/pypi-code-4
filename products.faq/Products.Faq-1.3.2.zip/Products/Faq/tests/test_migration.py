import unittest2 as unittest
import transaction

from plone.app.testing import setRoles, TEST_USER_ID
from plone.testing.z2 import Browser

from Products.Faq.migrations import  upgrade_1000_to_1001
from Products.Faq.testing import PLONE_FAQ_INTEGRATION_TESTING

class MigrationTestCase(unittest.TestCase):

    layer = PLONE_FAQ_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        if 'faqs' in self.portal:
            del self.portal['faqs']

    def test_btree_migration(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('FaqFolder', 'faqs', title='FAQ Folder')
        faqs = self.portal['faqs']
        faqs.reindexObject()
        delattr(faqs, '_tree')
        upgrade_1000_to_1001(self.portal['portal_setup'])
        self.assertTrue(hasattr(faqs, '_tree'))


class ContentTestCase(unittest.TestCase):

    layer = PLONE_FAQ_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        if 'faqs' in self.portal:
            del self.portal['faqs']
            transaction.commit()

    def test_faqfolder(self):
        self.assertIn('FaqFolder', self.portal.portal_types)

    def test_faqentry(self):
        self.assertIn('FaqEntry', self.portal.portal_types)

    def test_view(self):
        browser = Browser(self.layer['app'])

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('FaqFolder', 'faqs', title='FAQ Folder')
        self.portal['faqs'].invokeFactory('FaqEntry', 'faq1', title='What is it?')
        faqentry = self.portal['faqs']['faq1']
        transaction.commit()

        browser.handleErrors = False
        browser.open(faqentry.absolute_url())
        self.assertIn('What is it?', browser.contents)
