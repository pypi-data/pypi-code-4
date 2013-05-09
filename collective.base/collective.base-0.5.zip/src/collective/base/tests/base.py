from Testing import ZopeTestCase as ztc
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import z2
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides
from zope.publisher.browser import TestRequest

import mock
import unittest


class CollectiveBaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""

        # Required by Products.CMFPlone:plone-content to setup defaul plone site.
        z2.installProduct(app, 'Products.PythonScripts')

        # Load ZCML
        import collective.base
        self.loadZCML(package=collective.base)

    def setUpPloneSite(self, portal):
        """Set up Plone."""

        # Installs all the Plone stuff. Workflows etc. to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'Products.PythonScripts')


FIXTURE = CollectiveBaseLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="CollectiveBaseLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="CollectiveBaseLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        ztc.utils.setupCoreSessions(self.layer['app'])
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def create_view(self, view, context=None):
        if context is None:
            context = self.portal
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        request.set = mock.Mock()
        return view(context, request)


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
