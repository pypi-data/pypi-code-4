#coding=utf8
from .config import PACKAGE_NAME
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from Products.CMFCore.utils import getToolByName


class PackageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        pass

    def setUpPloneSite(self, portal):
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setChainForPortalTypes(
            ['News Item', 'Document', 'Link'],
            ['simple_publication_workflow']
        )


FIXTURE = PackageLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='{}:Integration'.format(PACKAGE_NAME)
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='{}:Integration'.format(PACKAGE_NAME)
)
