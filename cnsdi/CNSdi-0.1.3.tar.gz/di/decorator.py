"""
decorator.py

Contains decorator definitions for use.

Valid uses of @service are

  @service('id')
  def func(arg): pass

  @service('id')
  class I(object): pass

Valid uses of @inject are

  @inject(['id1','id2'])
  def func(a,b): pass

  class O(object):
    @inject(['id1','id2'])
    def __init__(self,a,b): pass
"""

import inspect
from di import ServiceStore

class Servicer(object):
    """@service decoration"""
    def __init__(self, id, store=ServiceStore, ns='default'):
        self.id = id
        self.store = store
        self.namespace = ns

    def __call__(self, f):
        if inspect.isclass(f):
            self.store.add_service(self.id, f(), to_namespace=self.namespace)
        else:
            self.store.add_service(self.id, f, to_namespace=self.namespace)

        return f

class Injector(object):
    """@inject decoration"""
    def __init__(self, list_of_service_ids, store=ServiceStore, ns='default'):
        self.ids = list_of_service_ids
        self.store = store
        self.namespace = ns

    # TODO: figure out a better way to hint arguments
    def __call__(self, f):
        if 'self' in inspect.getargspec(f).args:
            def new_f(s, *args, **kwargs):
                _args = []
                for service in self.get_services():
                    _args.append(service)
                for arg in args:
                    _args.append(arg)
                return f(s, *_args, **kwargs)
            return new_f
        else:
            def new_f(*args, **kwargs):
                _args = []
                for service in self.get_services():
                    _args.append(service)
                for arg in args:
                    _args.append(arg)
                return f(*_args, **kwargs)
            return new_f

    def get_services(self):
        """helper function to get injected services"""
        for id in self.ids:
            yield self.store.get_service(id, from_namespace=self.namespace)

service = Servicer
inject = Injector