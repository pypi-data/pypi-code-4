from plone import api
from plone.browserlayer.utils import registered_layers

from seantis.people import tests
from seantis.people import interfaces


class TestSetup(tests.IntegrationTestCase):

    def test_profile_installed(self):
        setup = api.portal.get_tool('portal_setup')
        version = setup.getLastVersionForProfile('seantis.people:default')

        self.assertNotEqual(version, None)
        self.assertNotEqual(version, 'unknown')

    def test_request_layer_active(self):
        layers = registered_layers()
        self.assertIn(interfaces.ISeantisPeopleSpecific, layers)
