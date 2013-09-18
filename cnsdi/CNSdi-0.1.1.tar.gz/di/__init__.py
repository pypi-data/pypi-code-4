"""
The dependency injection module contains everything you need
to store and lookup services, and to inject them into functions,
including class functions.
"""
from collections import namedtuple
from base64 import b16encode
from exceptions import ServiceNotFound

Service = namedtuple('Service', 'ns, id, service')

class ServiceStore(object):
    """Storage for all your services."""
    services = {}

    @classmethod
    def add_service(cls, id, service, to_namespace='default'):
        """Add a service with an id to ServiceStore"""
        service_hash = b16encode(to_namespace + id)
        cls.services[service_hash] = Service(to_namespace, id, service)

    @classmethod
    def get_service(cls, id, from_namespace='default'):
        """Get a service by id, raises a ServiceNotFound exception if the service id is not found."""
        service_hash = b16encode(from_namespace + id)
        if service_hash in cls.services.keys():
            return cls.services[service_hash].service
        else:
            raise ServiceNotFound("Service " + id + " not found.")
