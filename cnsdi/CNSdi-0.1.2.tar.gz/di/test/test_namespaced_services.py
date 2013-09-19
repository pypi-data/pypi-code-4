from unittest import TestCase
from di.helpers import get_service, add_service
from di.exceptions import ServiceNotFound

class TestNamespacedServices(TestCase):
    def setUp(self):
        def nsfunc(arg): pass
        add_service('nsfunc', nsfunc, ns='ns')

    def test_get_service_without_namespace_does_not_get_nsfunc(self):
        self.assertRaises(ServiceNotFound, get_service, 'nsfunc')

    def test_get_service_with_namespace_returns_nsfunc(self):
        self.assertEqual('nsfunc', get_service('nsfunc', ns='ns').__name__)