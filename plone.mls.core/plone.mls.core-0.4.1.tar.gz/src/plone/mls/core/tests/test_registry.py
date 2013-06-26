# -*- coding: utf-8 -*-
"""Test Registry for plone.mls.core."""

# python imports
import unittest2 as unittest

# zope imports
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

# local imports
from plone.mls.core.interfaces import IMLSSettings
from plone.mls.core.testing import PLONE_MLS_CORE_INTEGRATION_TESTING


class TestMLSRegistry(unittest.TestCase):
    """Registry Test Case for plone.mls.core."""
    layer = PLONE_MLS_CORE_INTEGRATION_TESTING

    def test_registry_registered(self):
        """Test that the settings are registered correctly."""
        registry = getUtility(IRegistry)
        self.assertTrue(registry.forInterface(IMLSSettings))

    def test_mls_registry_agency_id(self):
        """Test for the 'agency_id' key and the default value."""
        registry = getUtility(IRegistry)
        key = 'plone.mls.core.interfaces.IMLSSettings.agency_id'
        self.assertTrue(key in registry.records.keys())
        self.assertEquals(registry.records.get(key).value, u'')

    def test_mls_registry_mls_key(self):
        """Test for the 'mls_key' key and the default value."""
        registry = getUtility(IRegistry)
        key = 'plone.mls.core.interfaces.IMLSSettings.mls_key'
        self.assertTrue(key in registry.records.keys())
        self.assertEquals(registry.records.get(key).value, u'')

    def test_mls_registry_mls_site(self):
        """Test for the 'mls_site' key and the default value."""
        registry = getUtility(IRegistry)
        key = 'plone.mls.core.interfaces.IMLSSettings.mls_site'
        self.assertTrue(key in registry.records.keys())
        self.assertEquals(registry.records.get(key).value, u'')
