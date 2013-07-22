from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting, FunctionalTesting

import collective.checktranslated

CHECKTRANSLATED = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.checktranslated,
    additional_z2_products=(),
    gs_profile_id='collective.checktranslated:default',
    name="CHECKTRANSLATED")

CHECKTRANSLATED_INTEGRATION = IntegrationTesting(
    bases=(CHECKTRANSLATED,), name="CHECKTRANSLATED_INTEGRATION")


CHECKTRANSLATED_FUNCTIONAL = FunctionalTesting(
    bases=(CHECKTRANSLATED,), name="CHECKTRANSLATED_FUNCTIONAL")
