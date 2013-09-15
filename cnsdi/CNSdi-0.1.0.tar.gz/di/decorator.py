__author__ = 'sscoble'

import inspect
from di import ServiceStore

class Servicer(object):
    def __init__(self, id, store=ServiceStore):
        self.id = id
        self.store = store

    def __call__(self, f):
        if inspect.isclass(f):
            self.store.add_service(self.id, f())
        else:
            self.store.add_service(self.id, f)

        return f

class Injector(object):
    def __init__(self, list_of_service_ids, store=ServiceStore):
        self.ids = list_of_service_ids
        self.store = store

    def __call__(self, f):
        if 'self' in inspect.getargspec(f).args:
            def new_f(s):
                return f(s, *self.get_services())
            return new_f
        else:
            def new_f():
                return f(*self.get_services())
            return new_f

    def get_services(self):
        for id in self.ids:
            yield self.store.get_service(id)

service = Servicer
inject = Injector