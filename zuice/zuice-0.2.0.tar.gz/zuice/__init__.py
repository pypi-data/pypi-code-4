import itertools

import zuice.reflect
from .bindings import Bindings

__all__ = ['Bindings', 'Injector', 'Base', 'dependency']

class Injector(object):
    def __init__(self, bindings):
        self._bindings = bindings.copy()
        self._bindings.bind(Injector).to_instance(self)
    
    def get(self, key):
        if key in self._bindings:
            return self._bindings[key](self)
            
        elif isinstance(key, type):
            return self._get_from_type(key)
        
        else:
            raise NoSuchBindingException(key)
    
    def _get_from_type(self, type_to_get):
        if hasattr(type_to_get.__init__, 'zuice'):
            return self._inject(type_to_get, type_to_get.__init__.zuice)
        if zuice.reflect.has_no_arg_constructor(type_to_get):
            return type_to_get()
        raise NoSuchBindingException(type_to_get)
    
    def _inject(self, to_call, argument_builder):
        args, kwargs = argument_builder.build_args(self)
        return to_call(*args, **kwargs)
    
class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)


class Dependency(object):
    _counter = itertools.count()
    
    def __init__(self, key):
        self._key = key
        self._ordering = self._counter.next()
        
    def inject(self, injector):
        return injector.get(self._key)

def dependency(key):
    return Dependency(key)

class InjectableConstructor(object):
    def build_args(self, injector):
        return [], {"___injector": injector}

class Base(object):
    def __init__(self, *args, **kwargs):
        attrs = []
        for key in dir(type(self)):
            attr = getattr(self, key)
            if isinstance(attr, Dependency):
                attrs.append((key, attr))
            
        if '___injector' in kwargs:
            injector = kwargs.pop('___injector')
            for key, attr in attrs:
                setattr(self, key, attr.inject(injector))
        else:
            if len(args) > len(attrs):
                raise TypeError(
                    "__init__ takes exactly %s arguments (%s given)" %
                        (len(attrs) + 1, len(args) + 1)
                )
            attrs.sort(key=lambda (key, attr): attr._ordering)
            for index, (key, attr) in enumerate(attrs):
                arg_name = key.lstrip("_");
                
                if index < len(args):
                    if arg_name in kwargs:
                        raise TypeError("Got multiple values for keyword argument '%s'" % arg_name)
                    setattr(self, key, args[index])
                elif arg_name in kwargs:
                    setattr(self, key, kwargs.pop(arg_name))
                else:
                    raise TypeError("Missing keyword argument: %s" % key)
        
        if len(kwargs) > 0:
            raise TypeError("Unexpected keyword argument: " + kwargs.items()[0][0])
    
    __init__.zuice = InjectableConstructor()
