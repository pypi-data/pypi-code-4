################################################################
# vs.org (C) 2011, Veit Schiele
################################################################


import unittest2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import quickInstallProduct
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles, login
from plone.testing import z2

from zope.configuration import xmlconfig
from AccessControl.SecurityManagement import newSecurityManager

import vs.org
import Products.ATVocabularyManager
import Products.DataGridField
import Products.MasterSelectWidget
try:
    import Products.LinguaPlone
    HAVE_LP = True
except ImportError:
    HAVE_LP = False
        
from AccessControl.SecurityManagement import newSecurityManager

class VsOrgFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.file('configure.zcml', Products.DataGridField, context=configurationContext)
        xmlconfig.file('configure.zcml', Products.MasterSelectWidget, context=configurationContext)
        xmlconfig.file('configure.zcml', Products.ATVocabularyManager, context=configurationContext)
        if HAVE_LP:
            xmlconfig.file('configure.zcml', Products.LinguaPlone, context=configurationContext)
        xmlconfig.file('configure.zcml', vs.org, context=configurationContext)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.DataGridField')
        z2.installProduct(app, 'Products.ATVocabularyManager')
        z2.installProduct(app, 'Products.MasterSelectWidget')
        z2.installProduct(app, 'Products.DataGridField')
        if HAVE_LP:
            z2.installProduct(app, 'Products.LinguaPlone')
        z2.installProduct(app, 'vs.org')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        quickInstallProduct(portal, 'Products.DataGridField')
        quickInstallProduct(portal, 'Products.ATVocabularyManager')
        quickInstallProduct(portal, 'Products.MasterSelectWidget')
        if HAVE_LP:
            quickInstallProduct(portal, 'Products.LinguaPlone')
        applyProfile(portal, 'vs.org:default')
        portal.acl_users.userFolderAddUser('god', 'dummy', ['Manager'], []) 
        setRoles(portal, 'god', ['Manager'])
        login(portal, 'god')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'vs.org')


VS_ORG_FIXTURE = VsOrgFixture()
VS_ORG_INTEGRATION_TESTING = IntegrationTesting(bases=(VS_ORG_FIXTURE,), name="VsOrgFixture:Integration")

class TestBase(unittest2.TestCase):

    layer = VS_ORG_INTEGRATION_TESTING

    @property
    def portal(self):
        return self.layer['portal']

    def login(self):
        """ Login as manager """
        user = self.portal.acl_users.getUser('god')
        newSecurityManager(None, user.__of__(self.portal.acl_users))

