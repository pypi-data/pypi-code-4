# -*- coding: utf-8 -*-
# $Id: common.py 117038 2010-05-07 09:47:23Z glenfant $
"""Unit tests common resources"""

from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    """
    fiveconfigure.debug_mode = True
    import aws.pdfbook
    zcml.load_config('configure.zcml', aws.pdfbook)
    fiveconfigure.debug_mode = False
    return

setup_product()

ptc.setupPloneSite(extension_profiles=('aws.pdfbook:default',))

class TestCaseMixin(object):

    def makeBaseContent(self):
        """Build content for our tests
        """
        self.loginAsPortalOwner()
        folder = self.portal.invokeFactory('Folder', id='sample')
        folder = self.portal[folder]
        _ = folder.invokeFactory('Document', id='doc', title="Doc title", description="Doc description")
        _ = folder[_]
        _.edit(text='<div>Doc body</div>')
        self.folder = folder
        self.logout()
        return

class PDFBookTestCase(ptc.PloneTestCase, TestCaseMixin):
    def afterSetUp(self):
        self.makeBaseContent()
        return

class PDFBookFunctionalTestCase(ptc.FunctionalTestCase, TestCaseMixin):
    def afterSetUp(self):
        super(PDFBookFunctionalTestCase, self).afterSetUp()
        self.makeBaseContent()
        self.browser = Browser()
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.site_props = self.ptool.site_properties
        return

    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()
        return

