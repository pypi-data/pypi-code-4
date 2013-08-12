from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2


class PloneFaq(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)


    def setUpZope(self, app, configurationContext):
        import Products.Faq
        self.loadZCML(package=Products.Faq)
        z2.installProduct(app, 'Products.Faq')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'Products.Faq:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.Faq')


PLONE_FAQ_FIXTURE = PloneFaq()
PLONE_FAQ_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_FAQ_FIXTURE,),
    name="PloneFaq:Integration")
PLONE_FAQ_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_FAQ_FIXTURE,),
    name="PloneFaq:Functional")

