# -*- coding: utf-8 -*-
from zope.configuration import xmlconfig
from plone.testing import z2
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login


class ContentruleSubscription(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.contentrules.subscription
        xmlconfig.file('configure.zcml',
                       collective.contentrules.subscription,
                       context=configurationContext)
        z2.installProduct(app, 'collective.contentrules.subscription')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.contentrules.subscription:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])
        portal.invokeFactory('Folder',
                             'folder-1',
                             title="Folder 1")


CONTENTRULESSUBSCRIPTION_FIXTURE = ContentruleSubscription()

CONTENTRULESSUBSCRIPTION_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(CONTENTRULESSUBSCRIPTION_FIXTURE, ),
                       name="ContentruleSubscription:Integration")
CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(CONTENTRULESSUBSCRIPTION_FIXTURE, ),
                       name="ContentruleSubscription:Functional")
