# -*- coding: utf-8 -*-
# $Id: test_setup.py 117038 2010-05-07 09:47:23Z glenfant $
"""Testing component setup in a Plone site"""

import common

from aws.pdfbook.interfaces import IPDFOptions

class SetupTestCase(common.PDFBookTestCase):

    def test_quickinstaller(self):
        """Are we correcttly registered/installed by quickinstaller
        """
        qi = self.portal.portal_quickinstaller
        self.failUnless(qi.isProductInstalled('aws.pdfbook'))
        return

    def test_propertysheet(self):
        """We have a propertysheet
        """
        props = self.portal.portal_properties
        self.failUnless(props.hasObject('aws_pdfbook_properties'))
        return

    def test_checkenabled(self):
        """Testing we're enabled on default content
        """
        enabled = self.portal.restrictedTraverse('@@aws.pdfbook.enabled')
        self.failUnless(enabled)
        return

    def test_setup(self):
        """Testing the standard setup
        """
        portal_options = IPDFOptions(self.portal)
        expected = set((u'File', u'Image'))
        got = set(portal_options.disallowed_types)
        self.failUnlessEqual(got, expected)
        self.failUnlessEqual(portal_options.recode_path, u'/usr/bin/recode')
        self.failUnlessEqual(portal_options.htmldoc_path, u'/usr/bin/htmldoc')
        return


def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SetupTestCase))
    return suite
