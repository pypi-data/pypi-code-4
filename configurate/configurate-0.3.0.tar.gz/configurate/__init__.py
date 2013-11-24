from __future__ import absolute_import

from collections import Mapping, MutableMapping
from string import Formatter

from .version import version as __version__

if 'basestring' not in __builtins__:
    # Python 3 doesn't have a separate "basestring" base class.
    basestring = str


class Configurate(MutableMapping):

    _formatter = Formatter()
    _instance_attrs = [
        '_raw',
        '_parent',
        '_root',
        '_interpolate',
    ]

    def __init__(self, mapping=None, _parent=None, _interpolate=True, **kwargs):
        # __setattr__() uses __dict__ to know what attributes to treat as normal attributes instead of config keys.
        # To be able to use normal "self.attr = X" syntax for the rest of __init__(), it's convenient to prime
        # __dict__ up front.
        self.__dict__.update(dict.fromkeys(self._instance_attrs))
        self._raw = {}

        self._parent = _parent
        if self._parent:
            self._root = self._parent._root
        else:
            self._root = self
            self._interpolate = _interpolate

        if mapping:
            self.merge(mapping)
        self.merge(kwargs)

    def merge(self, mapping):
        if isinstance(mapping, Configurate):
            mapping = mapping.to_dict(interpolate=False)

        for key, value in mapping.items():
            self._check_is_attribute(key)
            if isinstance(value, Mapping):
                if not isinstance(self.get(key, None), Configurate):
                    self._raw[key] = Configurate(_parent=self)
                self[key].merge(value)
            else:
                self[key] = value

    def __getitem__(self, key, interpolate=None):
        if interpolate is None:
            interpolate = self._root._interpolate

        value = self._raw[key]
        if interpolate and isinstance(value, basestring):
            needed_keys = set(
                [parsed[1].split('.')[0].split('[', 1)[0] for parsed in self._formatter.parse(value) if parsed[1]]
            )
            value = self._formatter.vformat(
                value,
                [],
                {
                    needed_key: self._find_value(needed_key, skip_first=(key == needed_key))
                    for needed_key in needed_keys
                },
            )
        return value

    def _check_is_attribute(self, key, exc_class=KeyError):
        if key in self.__dict__ or key in dir(type(self)):
            raise exc_class(
                '{key!r} is a restricted key: it is an instance'
                'attribute of {self.__class__.__name__}'.format(**locals())
            )

    def __setitem__(self, key, value):
        self._check_is_attribute(key)
        if isinstance(value, Mapping):
            if isinstance(value, Configurate):
                value = value.to_dict(interpolate=False)
            self.pop(key)
            self.merge({key: value})
        else:
            self._raw[key] = value

    def __delitem__(self, key):
        self._check_is_attribute(key)
        del(self._raw[key])

    def __iter__(self):
        return iter(self._raw)

    def __len__(self):
        return len(self._raw)

    def __getattr__(self, key):
        # _raw may not be present yet when unpickling.
        if '_raw' in self.__dict__ and key in self._raw:
            return self[key]
        else:
            raise AttributeError(
                'AttributeError: {self.__class__.__name__!r} object has no attribute {key!r}'.format(self=self, key=key)
            )

    def __setattr__(self, key, value):
        if key in self.__dict__:
            super(Configurate, self).__setattr__(key, value)
        else:
            self._check_is_attribute(key, exc_class=AttributeError)
            self[key] = value

    def __dir__(self):
        return sorted(
            dir(type(self)) +
            self.__dict__.keys() +
            self._raw.keys()
        )

    def __repr__(self):
        return '{self.__class__.__name__}({self._raw!r})'.format(self=self)

    def get(self, key, default=None, interpolate=None):
        try:
            return self.__getitem__(key, interpolate=interpolate)
        except KeyError:
            return default

    def _find_value(self, key, skip_first=False):
        if not skip_first and key in self:
            return self[key]
        elif self._parent:
            return self._parent._find_value(key)
        else:
            raise KeyError('{key!r} not found in configuration parent traversal.'.format(key=key))

    def to_dict(self, interpolate=None):
        if interpolate is None:
            interpolate = self._root._interpolate

        result = {}
        for key in self:
            value = self.__getitem__(key, interpolate=interpolate)
            if hasattr(value, 'to_dict'):
                value = value.to_dict(interpolate=interpolate)
            result[key] = value
        return result
