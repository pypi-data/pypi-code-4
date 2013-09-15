from unittest import TestCase
from di.exceptions import ServiceNotFound
from di import ServiceStore

class TestExceptions(TestCase):

    def test_service_not_found_exception(self):
        self.assertRaises(ServiceNotFound, ServiceStore.get_service, 'does.not.exist')