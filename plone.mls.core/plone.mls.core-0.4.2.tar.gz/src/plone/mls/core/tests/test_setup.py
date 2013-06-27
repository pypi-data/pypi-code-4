# -*- coding: utf-8 -*-
"""Test Setup of plone.mls.core."""

# python imports
import unittest2 as unittest

# zope imports
from plone.browserlayer import utils as layerutils

# local imports
from plone.mls.core.browser.interfaces import IMLSSpecific
from plone.mls.core.testing import PLONE_MLS_CORE_INTEGRATION_TESTING


class TestSetup(unittest.TestCase):
    """Setup Test Case for plone.mls.core."""
    layer = PLONE_MLS_CORE_INTEGRATION_TESTING

    def test_plone_app_registry_installed(self):
        """Test that plone.app.registry is installed."""
        portal = self.layer['portal']
        qi = portal.portal_quickinstaller
        if qi.isProductAvailable('plone.app.registry'):
            self.assertTrue(qi.isProductInstalled('plone.app.registry'))
        else:
            self.assertTrue(
                'plone.app.registry' in qi.listInstallableProfiles())

    def test_browserlayer_installed(self):
        """Test that the browser layer is installed correctly."""
        self.assertTrue(IMLSSpecific in layerutils.registered_layers())
