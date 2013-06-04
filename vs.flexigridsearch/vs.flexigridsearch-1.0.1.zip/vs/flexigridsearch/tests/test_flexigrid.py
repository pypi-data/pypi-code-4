###############################################################
# vs.flexigridsearch (C) 2011, Veit Schiele
################################################################

import unittest2
from Products.CMFCore.utils import getToolByName
from base import TestBase

class FlexigridTests(TestBase):

    def testConfigurationProperties(self):
        pprops = getToolByName(self.portal, 'portal_properties')
        self.assertEqual('flexigridsearch_properties' in pprops.objectIds(), True)
        fs_props = pprops.flexigridsearch_properties.propertyIds()
        self.assertEqual('portalTypesToSearch' in fs_props, True)
        self.assertEqual('columns' in fs_props, True)
        self.assertEqual('sort_limit' in fs_props, True)
        self.assertEqual('max_hits_from_catalog' in fs_props, True)

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FlexigridTests))
    return suite
