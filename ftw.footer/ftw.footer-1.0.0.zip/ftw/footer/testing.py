from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from ftw.builder.testing import BUILDER_LAYER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwFooterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.footer

        xmlconfig.file('configure.zcml', ftw.footer,
                       context=configurationContext)
        z2.installProduct(app, 'ftw.footer')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.footer:default')


FTW_FOOTER_FIXTURE = FtwFooterLayer()
FTW_FOOTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FOOTER_FIXTURE, ), name="FtwFooter:Integration")
