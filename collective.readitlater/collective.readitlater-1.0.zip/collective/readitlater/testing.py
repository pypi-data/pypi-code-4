from plone.app.testing import *
import collective.readitlater


FIXTURE = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.readitlater,
    additional_z2_products=[],
    gs_profile_id='collective.readitlater:default',
    name="collective.readitlater:FIXTURE"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,), name="collective.readitlater:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,), name="collective.readitlater:Functional"
)
