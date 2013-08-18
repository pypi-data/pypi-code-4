
# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2


class CollectiveBehaviorLocalSkinLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.behavior.localskin
        self.loadZCML(package=collective.behavior.localskin)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "plone.app.dexterity:default")

        from plone.dexterity.fti import DexterityFTI
        fti = DexterityFTI("MicroSite")
        fti.title = u"MicroSite"
        fti.klass = "plone.dexterity.content.Container"
        fti.behaviors = (
            "plone.app.dexterity.behaviors.metadata.IBasic",
            "plone.app.content.interfaces.INameFromTitle",
            "collective.behavior.localregistry.behavior.ILocalRegistry",
            "collective.behavior.localskin.behavior.ILocalSkin",
        )
        portal.portal_types._setObject("MicroSite", fti)

    def testSetUp(self):
        # Invalidate Dexterity fti.lookupSchema() cache:
        import plone.dexterity.schema
        for name in dir(plone.dexterity.schema.generated):
            if name.startswith("plone"):
                delattr(plone.dexterity.schema.generated, name)
        plone.dexterity.schema.SCHEMA_CACHE.clear()


COLLECTIVE_BEHAVIOR_LOCALSKIN_FIXTURE =\
    CollectiveBehaviorLocalSkinLayer()

COLLECTIVE_BEHAVIOR_LOCALSKIN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_BEHAVIOR_LOCALSKIN_FIXTURE,),
    name="Integration")
COLLECTIVE_BEHAVIOR_LOCALSKIN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_BEHAVIOR_LOCALSKIN_FIXTURE,),
    name="Functional")
COLLECTIVE_BEHAVIOR_LOCALSKIN_ROBOT_TESTING = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE,
           COLLECTIVE_BEHAVIOR_LOCALSKIN_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="Robot")
