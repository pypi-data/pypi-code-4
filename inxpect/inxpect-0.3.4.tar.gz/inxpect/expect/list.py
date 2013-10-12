# -*- coding: utf8 -*-
from .property import DefaultProperty
from .getters import AtIndex
from . import operator


class ListMethod(DefaultProperty):
    def __call__(self, *expected):
        return self.has_all(expected)

    def has(self, expected, _getter_=None):
        return self._functor(operator.Contains, expected, _getter_)

    def has_key(self, expected, _getter_=None):
        return self.len.greater_than(expected, _getter_)

    def has_keys(self, expected, _getter_=None):
        return self.len.greater_than(max(expected), _getter_)

    def has_any_key(self, expected, _getter_=None):
        return self.len.greater_than(min(expected), _getter_)

    def has_all(self, expected, _getter_=None):
        return self._functor(operator.ContainsAll, expected, _getter_)

    def has_any(self, expected, _getter_=None):
        return self._functor(operator.ContainsAny, expected, _getter_)

    def at(self, position, _getter_=None):
        from .factory import DefaultMethodFactory
        _getter_ = self.get_finder(_getter_)
        return DefaultMethodFactory(_getter_=AtIndex(position, _getter_))


class ListItemMethod(ListMethod):
    def __call__(self, expected):
        return self.has(expected)
