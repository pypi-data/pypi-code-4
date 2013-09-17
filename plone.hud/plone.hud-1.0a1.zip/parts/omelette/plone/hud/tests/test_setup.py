# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone.hud.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of plone.hud into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if plone.hud is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('plone.hud'))

    def test_uninstall(self):
        """Test if plone.hud is cleanly uninstalled."""
        self.installer.uninstallProducts(['plone.hud'])
        self.assertFalse(self.installer.isProductInstalled('plone.hud'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneHudLayer is registered."""
        from plone.hud.interfaces import IPloneHudLayer
        from plone.browserlayer import utils
        self.failUnless(IPloneHudLayer in utils.registered_layers())
