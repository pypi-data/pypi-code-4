from zope.security.management import newInteraction, endInteraction
from seantis.plonetools.testlayer import INTEGRATION_TESTING

from seantis.plonetools.testing import TestCase

# to use with integration where security interactions need to be done manually
class IntegrationTestCase(TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        # setup security
        newInteraction()

    def tearDown(self):
        endInteraction()
        super(IntegrationTestCase, self).tearDown()
