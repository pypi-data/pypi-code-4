# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.contact.facetednav.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.contact.facetednav into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.contact.facetednav is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.contact.facetednav'))

    def test_uninstall(self):
        """Test if collective.contact.facetednav is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.contact.facetednav'])
        self.assertFalse(self.installer.isProductInstalled('collective.contact.facetednav'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveContactFacetednavLayer is registered."""
        from collective.contact.facetednav.interfaces import ICollectiveContactFacetednavLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveContactFacetednavLayer in utils.registered_layers())
