# -*- coding: utf8 -*-
from .property import DefaultProperty
from .operator import *



class DictMethod(DefaultProperty):
    def __call__(self, **expected_items):
        return self.has_items(expected_items)

    def has_key(self, expected, closure=None):
        return self.should(Contains, expected, closure)

    def has_keys(self, expected, closure=None):
        return self.should(ContainsAll, expected, closure)

    def has_any_key(self, expected, closure=None):
        return self.should(ContainsAny, expected, closure)

    def has_item(self, name, value, closure=None):
        return self.should(ContainsItem, (name, value), closure)

    def has_items(self, expected, closure=None):
        return self.should(ContainsAllItem, expected, closure)

    def has_any_item(self, expected, closure=None):
        return self.should(ContainsAnyItem, expected, closure)

    def has_value(self, expected, closure=None):
        return self.should(ContainsValue, expected, closure)

    def has_values(self, expected, closure=None):
        return self.should(ContainsAllValue, expected, closure)

    def has_any_value(self, expected, closure=None):
        return self.should(ContainsAnyValue, expected, closure)

    def at(self, key):
        from .factory import DefaultMethodFactory
        closure = self.should.closure(lambda _dict: _dict.get(key))
        return DefaultMethodFactory(getter=closure)


class DictItemMethod(DictMethod):
    def __call__(self, name, value):
        return self.has_item(name, value)
