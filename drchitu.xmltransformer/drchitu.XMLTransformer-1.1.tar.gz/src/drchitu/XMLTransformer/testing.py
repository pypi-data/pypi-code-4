from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class DrchituxmltransformerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import drchitu.XMLTransformer
        xmlconfig.file(
            'configure.zcml',
            drchitu.XMLTransformer,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'drchitu.XMLTransformer:default')

DRCHITU_XMLTRANSFORMER_FIXTURE = DrchituxmltransformerLayer()
DRCHITU_XMLTRANSFORMER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DRCHITU_XMLTRANSFORMER_FIXTURE,),
    name="DrchituxmltransformerLayer:Integration"
)
DRCHITU_XMLTRANSFORMER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DRCHITU_XMLTRANSFORMER_FIXTURE, z2.ZSERVER_FIXTURE),
    name="DrchituxmltransformerLayer:Functional"
)
