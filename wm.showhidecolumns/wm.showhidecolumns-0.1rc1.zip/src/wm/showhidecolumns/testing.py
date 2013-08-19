from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class WmshowhidecolumnsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import wm.showhidecolumns
        xmlconfig.file(
            'configure.zcml',
            wm.showhidecolumns,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'wm.showhidecolumns:default')

WM_SHOWHIDECOLUMNS_FIXTURE = WmshowhidecolumnsLayer()
WM_SHOWHIDECOLUMNS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(WM_SHOWHIDECOLUMNS_FIXTURE,),
    name="WmshowhidecolumnsLayer:Integration"
)
