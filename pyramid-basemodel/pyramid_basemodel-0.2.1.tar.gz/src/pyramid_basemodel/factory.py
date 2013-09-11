# -*- coding: utf-8 -*-

"""Provides a configurable ``factory`` classmethod and configurable ``update``
  and ``__json__`` methods for sqlalchemy models.
"""

__all__ = [
    'FactoryMixin',
    'SimpleFactory',
    'SimplePropertyUpdater',
    'SimplePropertyJSONRepresenter',
    'orm_config',
]

import logging
logger = logging.getLogger(__name__)

import venusian
import zope.component
import zope.interface

from pyramid_basemodel.interfaces import IDeclarativeBase

class IORMFactoryMethod(zope.interface.Interface):
    """Marker interface provided by ORM method adapters."""


class orm_config(object):
    """Configuration decorator for registering ORM method implementations, e.g.::
      
          @implementer(IFoo)
          class Foo(object): pass
          
          @orm_config('factory', IFoo)
          class FooFactory(object):
              def __call__(self, request):
                  return self.model_cls()
              def __init__(self, model_cls):
                  self.model_cls = model_cls
      
      Following a venusian scan, you can then use::
      
          foo = Foo.factory(request)
      
    """
    
    def __init__(self, method_name, context, **kwargs):
        self.method_name = method_name
        self.context = context
    
    def register(self, scanner, name, wrapped, **kwargs):
        config = scanner.config
        context = config.maybe_dotted(self.context)
        adapters = config.registry.adapters
        depends = (context,)
        provides = kwargs.get('method_iface', IORMFactoryMethod)
        adapters.register(depends, provides, self.method_name, wrapped)
    
    def __call__(self, wrapped, **kwargs):
        venusian = kwargs.get('venusian', venusian)
        venusian.attach(wrapped, self.register)
        return wrapped
    


class FactoryMixin(object):
    """Implements ``factory``, ``update`` and ``__json__`` methods that
      look for context specific adapters.
    """
    
    simple_properties = ()
    
    @classmethod
    def _lookup_orm_adapter(cls, request, context, name, **kwargs):
        """Lookup an adaptor that requires an interface provided by ``context``
          and ``provides`` a method interface.
        """
        
        # Compose.
        base_iface = kwargs.get('base_iface', IDeclarativeBase)
        error_cls = kwargs.get('error_cls', zope.component.ComponentLookupError)
        implementedBy = kwargs.get('implementedBy', zope.interface.implementedBy)
        providedBy = kwargs.get('providedBy', zope.interface.providedBy)
        provides = kwargs.get('provides', IORMFactoryMethod)
        
        # Unpack.
        adapters = request.registry.adapters
        is_instance = base_iface.providedBy(context)
        context_iface = providedBy(context) if is_instance else implementedBy(context)
        
        # Try first to get an adapter for all of the interfaces provided by
        # context, then try each interface in turn.
        attempts = [context_iface] # all interfaces
        attempts += [iface for iface in context_iface.flattened()] # each in turn
        for iface in attempts:
            requires = (iface,)
            adapter = adapters.lookup(requires, provides, name=name, default=None)
            if adapter is not None:
                return adapter
        
        # If we got here, raise a component lookup error.
        raise error_cls(provides, name)
    
    
    @classmethod
    def factory(cls, request, *args, **kwargs):
        adapter_cls = cls._lookup_orm_adapter(request, cls, 'factory')
        adapter = adapter_cls(cls)
        return adapter(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        adapter_cls = self._lookup_orm_adapter(request, self, 'update')
        adapter = adapter_cls(self)
        return adapter(request, *args, **kwargs)
    
    def __json__(self, request):
        adapter_cls = self._lookup_orm_adapter(request, self, '__json__')
        adapter = adapter_cls(self)
        return adapter(request)
    


@orm_config('factory', IDeclarativeBase)
class SimpleFactory(object):
    """Instantiate and return a class instance."""
    
    def __call__(self, request, data):
        instance = self.model_cls()
        instance.update(request, data)
        return instance
    
    def __init__(self, model_cls):
        self.model_cls = model_cls
    


@orm_config('update', IDeclarativeBase)
class SimplePropertyUpdater(object):
    """Utility to update a model instance's simple properties"""
    
    def __call__(self, request, data):
        instance = self.instance
        for key in instance.simple_properties:
            if data.has_key(key):
                setattr(instance, key, data[key])
    
    def __init__(self, instance):
        self.instance = instance
    


@orm_config('json', IDeclarativeBase)
class SimplePropertyJSONRepresenter(object):
    """Utility to represent a model instance's simple properties as a json dict."""
    
    def __json__(self, request):
        instance = self.instance
        data = {}
        for key in instance.simple_properties:
            data[key] = getattr(instance, key)
        return data
    
    def __init__(self, instance):
        self.instance = instance
    

