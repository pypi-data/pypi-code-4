__author__ = 'sscoble'

from di import ServiceStore

def get_service(id):
    return ServiceStore.get_service(id)

def add_service(id, service):
    ServiceStore.add_service(id, service)
