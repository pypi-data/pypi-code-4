# -*- coding: utf-8 -*-
from Products.Doormat.testing import PRODUCTS_DOORMAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import applyProfile

import unittest2 as unittest


class DoormatUninstallTest(unittest.TestCase):
    """Test that product uninstalls cleanly."""

    layer = PRODUCTS_DOORMAT_INTEGRATION_TESTING

    def createMoreTestingContent(self):
        self.portal.invokeFactory("Doormat", 'extra-doormat')

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.types = self.portal.portal_types
        self.createMoreTestingContent()
        applyProfile(self.portal, 'Products.Doormat:uninstall')

    def test_contenttypes_uninstalled(self):
        self.assertFalse('Doormat' in self.types.objectIds())
        self.assertFalse('DoormatColumn' in self.types.objectIds())
        self.assertFalse('DoormatSection' in self.types.objectIds())
        self.assertFalse('DoormatReference' in self.types.objectIds())
        self.assertFalse('DoormatCollection' in self.types.objectIds())
        self.assertFalse('DoormatMixin' in self.types.objectIds())

    def test_browserlayer_unavailable(self):
        from plone.browserlayer import utils
        from Products.Doormat.browser.interfaces import IDoormatLayer
        self.assertFalse(
            IDoormatLayer in utils.registered_layers()
        )

    def test_css_unregistered(self):
        cssreg = getattr(self.portal, 'portal_css')
        stylesheets_ids = cssreg.getResourceIds()
        self.assertFalse(
            '++resource++Products.Doormat.stylesheets/doormat.css' in
            stylesheets_ids)

    def test_default_doormat_removed(self):
        self.assertFalse('doormat' in self.portal.objectIds())

    def test_extra_doormat_removed(self):
        self.assertFalse('extra-doormat' in self.portal.objectIds())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
