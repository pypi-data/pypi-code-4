from unittest import TestCase
from di.helpers import get_service, add_service
from di import ServiceStore

class O(object): pass

class TestHelpers(TestCase):
    def setUp(self):
        ServiceStore.add_service('object', O)

    def test_get_service_returns_class(self):
        service = get_service('object')
        self.assertEqual(O, service, "Incorrect service found.")

    def test_add_service(self):
        add_service('O', O)
        self.assertEqual(O, ServiceStore.get_service('O'), "Incorrect service found.")