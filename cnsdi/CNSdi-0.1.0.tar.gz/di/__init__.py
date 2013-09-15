__author__ = 'sscoble'

from exceptions import ServiceNotFound

class ServiceStore(object):
    services = {}

    @classmethod
    def add_service(cls, id, service):
        cls.services[id] = service

    @classmethod
    def get_service(cls, id):
        if id in cls.services.keys():
            return cls.services[id]
        else:
            raise ServiceNotFound("Service " + id + " not found.")
