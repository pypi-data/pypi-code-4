# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.app.testing import setRoles, TEST_USER_ID
from Products.Faq.testing import PLONE_FAQ_INTEGRATION_TESTING


class RolemapTestCase(unittest.TestCase):

    layer = PLONE_FAQ_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_faq_roles(self):
        folder_roles = [r['name'] for r in self.portal.rolesOfPermission('Products.Faq: Add FaqFolder') if r['selected']]
        self.assertEqual(folder_roles, ['Contributor', 'Manager', 'Site Administrator'])
        faq_roles = [r['name'] for r in self.portal.rolesOfPermission('Products.Faq: Add FaqEntry') if r['selected']]
        self.assertEqual(folder_roles, ['Contributor', 'Manager', 'Site Administrator'])
