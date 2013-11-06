# from Products.DateRecurringIndex.testing import DRI_FIXTURE
from Products.CMFPlone.utils import getFSVersionTuple
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.formwidget.datetime.testing import PFWDT_FIXTURE
from plone.testing import z2


PLONE5 = getFSVersionTuple()[0] >= 5


class PFWDTATLayer(PloneSandboxLayer):

    # TODO: DRI_FIXTURE temporary until removal of DRI
    # defaultBases = (DRI_FIXTURE, PFWDT_FIXTURE,)
    defaultBases = (PFWDT_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.formwidget.datetime.at
        self.loadZCML(package=plone.formwidget.datetime.at)

        import plone.formwidget.datetime.at.tests.examples
        self.loadZCML(package=plone.formwidget.datetime.at.tests.examples)

        z2.installProduct(app, 'Products.ATContentTypes')

        # Install product and call its initialize() function
        z2.installProduct(app, 'plone.formwidget.datetime.at.tests.examples')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        if PLONE5:
            # Install Products.ATContentTypes profile only for versions, where
            # it's available
            self.applyProfile(portal, 'Products.ATContentTypes:default')

        self.applyProfile(
            portal,
            'plone.formwidget.datetime.at.tests.examples:examples')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'plone.formwidget.datetime.at.tests.examples')


PFWDTAT_FIXTURE = PFWDTATLayer()
PFWDTAT_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PFWDTAT_FIXTURE,),
        name="PFWDTAT:Integration")
