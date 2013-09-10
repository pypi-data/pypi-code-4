# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from redturtle.gritterize.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of redturtle.gritterize into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if redturtle.gritterize is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('redturtle.gritterize'))

    def test_uninstall(self):
        """Test if redturtle.gritterize is cleanly uninstalled."""
        self.installer.uninstallProducts(['redturtle.gritterize'])
        self.assertFalse(self.installer.isProductInstalled('redturtle.gritterize'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IRedturtleGritterizeLayer is registered."""
        from redturtle.gritterize.interfaces import IRedturtleGritterizeLayer
        from plone.browserlayer import utils
        self.failUnless(IRedturtleGritterizeLayer in utils.registered_layers())
