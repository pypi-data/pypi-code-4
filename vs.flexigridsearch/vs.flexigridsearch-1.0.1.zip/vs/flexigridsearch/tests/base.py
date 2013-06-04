################################################################
# vs.flexgridsearch (C) 2011, Veit Schiele
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

import vs.flexigridsearch
from AccessControl.SecurityManagement import newSecurityManager

class FlexigridFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.file('configure.zcml', vs.flexigridsearch, context=configurationContext)
        z2.installProduct(app, 'vs.flexigridsearch')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'vs.flexigridsearch:default')
        portal.acl_users.userFolderAddUser('god', 'dummy', ['Manager'], []) 
        setRoles(portal, 'god', ['Manager'])
        login(portal, 'god')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'vs.flexigridsearch')


FLEXIGRID_FIXTURE = FlexigridFixture()
FLEXIGRID_INTEGRATION_TESTING = IntegrationTesting(bases=(FLEXIGRID_FIXTURE,), name="FlexigridFixture:Integration")

class TestBase(unittest2.TestCase):

    layer = FLEXIGRID_INTEGRATION_TESTING

    @property
    def portal(self):
        return self.layer['portal']

    def login(self):
        """ Login as manager """
        user = self.portal.acl_users.getUser('god')
        newSecurityManager(None, user.__of__(self.portal.acl_users))

