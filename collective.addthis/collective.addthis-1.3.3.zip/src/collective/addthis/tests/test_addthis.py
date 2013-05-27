# -*- coding: utf-8 -*-
import unittest2 as unittest
from collective.addthis.testing import ADDTHIS_INTEGRATION_TESTING
from collective.addthis.testing import ADDTHIS_FUNCTIONAL_TESTING
from collective.addthis.interfaces import IAddThisSettings
from Products.CMFCore.utils import getToolByName
from plone.registry import Registry
from plone.testing.z2 import Browser


class IntegrationTest(unittest.TestCase):

    layer = ADDTHIS_INTEGRATION_TESTING

    def setUp(self):
        ''' Initialize the portal '''
        self.portal = self.layer['portal']
        self.registry = Registry()
        self.registry.registerInterface(IAddThisSettings)

    def test_is_addthis_installed(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('collective.addthis'))

    def test_are_resources_registered(self):
        js = getToolByName(self.portal, 'portal_javascripts')
        css = getToolByName(self.portal, 'portal_css')
        self.assertTrue('++resource++collective.addthis/addthis.js' in
            js.getResourceIds())
        self.assertTrue('++resource++collective.addthis/addthis.css' in
            css.getResourceIds())


class FunctionalTest(unittest.TestCase):

    layer = ADDTHIS_FUNCTIONAL_TESTING

    def setUp(self):
        ''' Initialize the portal '''
        self.portal = self.layer['portal']

    def test_is_addthis_visible(self):
        browser = Browser(self.portal)
        browser.open(self.portal.absolute_url())
        self.assertTrue('http://www.addthis.com/bookmark.php?v=250'\
            in browser.contents)
