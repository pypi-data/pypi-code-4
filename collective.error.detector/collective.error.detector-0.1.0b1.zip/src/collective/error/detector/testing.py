from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.error.detector


COLLECTIVE_ERROR_DETECTOR = PloneWithPackageLayer(
    zcml_package=collective.error.detector,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.error.detector:testing',
    name="COLLECTIVE_ERROR_DETECTOR")

COLLECTIVE_ERROR_DETECTOR_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_ERROR_DETECTOR, ),
    name="COLLECTIVE_ERROR_DETECTOR_INTEGRATION")

COLLECTIVE_ERROR_DETECTOR_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_ERROR_DETECTOR, ),
    name="COLLECTIVE_ERROR_DETECTOR_FUNCTIONAL")
