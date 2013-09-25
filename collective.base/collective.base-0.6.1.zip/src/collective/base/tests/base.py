from Testing import ZopeTestCase as ztc
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import z2

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
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def create_atcontent(self, ctype, parent=None, **kwargs):
        """Create instance of AT content type"""
        if parent is None:
            parent = self.portal
        content = parent[parent.invokeFactory(ctype, **kwargs)]
        content.reindexObject()
        return content

    def create_view(self, view, context=None):
        """Return instance of view

        :param view: View class
        :type view: class

        :param context: Context instance
        :type: context: obj

        :rtype: obj
        """
        if context is None:
            context = self.portal
        return view(context, self.request)

    def create_viewlet(self, viewlet, context=None, view=None, manager=None):
        """Return instance for viewlet

        :param viewlet: Viewlet class
        :type viewlet: class

        :param context: Context instance
        :type context: obj

        :param view: View instance
        :type view: obj

        :param manager: Viewlet manager instance
        :type manager: obj

        :rtype: obj
        """
        if context is None:
            context = self.portal
        return viewlet(context, self.request, view, manager)


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
