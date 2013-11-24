from __future__ import absolute_import

from itertools import chain
from collections import Mapping
from string import Formatter

from .version import version as __version__

if 'basestring' not in __builtins__:
    # Python 3 doesn't have a separate "basestring" base class.
    basestring = str


class Configurate(Mapping):

    _formatter = Formatter()

    def __init__(self, mapping=None, _parent=None, _interpolate=True, **kwargs):
        self._raw = {}

        self._parent = _parent
        if self._parent:
            self._root = self._parent._root
        else:
            self._root = self
            self._interpolate = _interpolate

        for key, value in chain(kwargs.items(), mapping.items() if mapping else ()):
            self._raw[key] = Configurate(value, _parent=self) if isinstance(value, Mapping) else value

    def __getitem__(self, key, interpolate=None):
        if interpolate is None:
            interpolate = self._root._interpolate

        value = self._raw[key]
        if interpolate and isinstance(value, basestring):
            needed_keys = [parsed[1] for parsed in self._formatter.parse(value) if parsed[1]]
            value = self._formatter.vformat(
                value,
                [],
                {
                    needed_key: self._find_value(needed_key, skip_first=(key == needed_key))
                    for needed_key in needed_keys
                },
            )
        return value

    def __iter__(self):
        return iter(self._raw)

    def __len__(self):
        return len(self._raw)

    def __getattr__(self, key):
        if key in self._raw:
            return self[key]
        else:
            raise AttributeError(
                'AttributeError: {self.__class__.__name__!r} object has no attribute {key!r}'.format(self=self, key=key)
            )

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
