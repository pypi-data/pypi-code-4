from collective.editmodeswitcher.testing import PACKAGE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from pyquery import PyQuery
from unittest2 import TestCase


class TestIntegration(TestCase):

    layer = PACKAGE_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

        self.portal_url = self.layer['portal'].absolute_url()

    def is_editable(self):
        doc = PyQuery(self.browser.contents)
        return len(doc('.documentEditable')) > 0

    def test_toggling_edit_mode(self):
        # The plone site should be "editable" by default for the site owner.
        self.browser.open(self.portal_url)
        self.assertTrue(
            self.is_editable(),
            'No ".documentEditable" found on site root. Markup changed?')

        # When we hit the "switch-editmode" view we are redirected back
        # to the context's default view:
        self.browser.open(self.portal_url + '/@@switch-editmode')
        self.assertEqual(
            self.portal_url, self.browser.url,
            'Expected to be redirected to the context\'s default view but'
            ' (site root in this case) but was not.')

        # and now the document is no longer editable:
        self.assertFalse(self.is_editable(), 'Site root still editable.')

        # even when reloading:
        self.browser.open(self.portal_url)
        self.assertFalse(self.is_editable(),
                         'Editable switch not persistent?')

        # when switching back on we are redirected to the default view again:
        self.browser.open(self.portal_url + '/@@switch-editmode')
        self.assertEqual(
            self.portal_url, self.browser.url,
            'Redirect seems to be wrong when re-enabling edit mode.')

        # and it is now editable again:
        self.assertTrue(self.is_editable(),
                        'Re-enabling the edit mode is not working.')
