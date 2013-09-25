# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.local.sentmail.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.local.sentmail into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.local.sentmail is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.local.sentmail'))

    def test_uninstall(self):
        """Test if collective.local.sentmail is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.local.sentmail'])
        self.assertFalse(self.installer.isProductInstalled('collective.local.sentmail'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveLocalSentmailLayer is registered."""
        from collective.local.sentmail.interfaces import ICollectiveLocalSentmailLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveLocalSentmailLayer in utils.registered_layers())
