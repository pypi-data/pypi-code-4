from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from zope.configuration import xmlconfig

class TestLayer(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):

        import seantis.plonetools
        xmlconfig.file(
            'configure.zcml',
            seantis.plonetools,
            context=configurationContext
        )
        self.loadZCML(package=seantis.plonetools)


TESTFIXTURE = TestLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(TESTFIXTURE, ),
    name="Testfixture:Integration"
)
