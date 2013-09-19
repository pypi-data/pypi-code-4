"""
helpers.py

Simple helpers for adding and getting a service
"""

from di import ServiceStore

def get_service(id, ns='default'):
    """Gets a service based on the id."""
    return ServiceStore.get_service(id, from_namespace=ns)

def add_service(id, service, ns='default'):
    """Adds a service with an id.  Same as di.decorator.service('id')(service)."""
    ServiceStore.add_service(id, service, to_namespace=ns)
