from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from zope.configuration import xmlconfig


class AddThisTests(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.z3cform
        xmlconfig.file('configure.zcml', plone.app.z3cform,
                       context=configurationContext)

        import plone.app.registry
        xmlconfig.file('configure.zcml', plone.app.registry,
                       context=configurationContext)

        import collective.addthis
        xmlconfig.file('configure.zcml', collective.addthis,
                       context=configurationContext)
        #self.loadZCML(name='configure.zcml', package=collective.addthis)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.z3cform:default')
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'collective.addthis:default')

#    def tearDownZope(self, app):
#        pass


ADDTHIS_FIXTURE = AddThisTests()
ADDTHIS_INTEGRATION_TESTING = IntegrationTesting(bases=(ADDTHIS_FIXTURE,),
    name="AddThisTests:Integration")
ADDTHIS_FUNCTIONAL_TESTING = FunctionalTesting(bases=(ADDTHIS_FIXTURE,),
    name="AddThisTests:Functional")
