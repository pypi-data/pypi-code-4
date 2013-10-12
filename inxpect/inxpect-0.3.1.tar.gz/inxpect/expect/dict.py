# -*- coding: utf8 -*-
from .property import DefaultProperty
from .getters import AtIndex
from . import operator



class DictMethod(DefaultProperty):
    def __call__(self, **expected_items):
        return self.has_items(expected_items)

    def has_key(self, expected, _getter_=None):
        return self._functor(operator.Contains, expected, _getter_)

    def has_keys(self, expected, _getter_=None):
        return self._functor(operator.ContainsAll, expected, _getter_)

    def has_any_key(self, expected, _getter_=None):
        return self._functor(operator.ContainsAny, expected, _getter_)

    def has_item(self, name, value, _getter_=None):
        return self._functor(operator.ContainsItem, (name, value), _getter_)

    def has_items(self, expected, _getter_=None):
        return self._functor(operator.ContainsAllItem, expected, _getter_)

    def has_any_item(self, expected, _getter_=None):
        return self._functor(operator.ContainsAnyItem, expected, _getter_)

    def has_value(self, expected, _getter_=None):
        return self._functor(operator.ContainsValue, expected, _getter_)

    def has_values(self, expected, _getter_=None):
        return self._functor(operator.ContainsAllValue, expected, _getter_)

    def has_any_value(self, expected, _getter_=None):
        return self._functor(operator.ContainsAnyValue, expected, _getter_)

    def at(self, key, _getter_=None):
        from .factory import DefaultMethodFactory
        _getter_ = self.get_finder(_getter_)
        return DefaultMethodFactory(_getter_=AtIndex(key, _getter_))


class DictItemMethod(DictMethod):
    def __call__(self, name, value):
        return self.has_item(name, value)
