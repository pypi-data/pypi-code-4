# -*- coding: utf-8 -*-
from Products.Doormat.testing import PRODUCTS_DOORMAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles

import unittest2 as unittest


class DoormatViewTest(unittest.TestCase):
    """Test with only default doormat content."""

    layer = PRODUCTS_DOORMAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.types = self.portal.portal_types

    def test_doormat_view(self):
        view = self.portal.doormat.restrictedTraverse('@@doormat-view')
        view()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
