# vim:fileencoding=utf-8
from functools import update_wrapper

def cached_property(f, name=None):
    """
    A decorator that caches the output of a method to the __dict__
    of the class instance.
    """
    if name is None:
        name = f.__name__ 
    def _get(self):
        try:
            return self.__dict__[name]
        except KeyError:
            value = f(self)
            self.__dict__[name] = value 
            return value
    update_wrapper(_get, f)
    def _set(self, value):
        self.__dict__[name] = value
    return property(_get, _set)

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
