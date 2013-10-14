# -*- coding: utf8 -*-
from .property import DefaultProperty
from .operator import Contains, ContainsAll, ContainsAny


class ListMethod(DefaultProperty):
    def __call__(self, *expected):
        return self.has_all(expected)

    def has(self, expected, closure=None):
        return self.should(Contains, expected, closure)

    def has_key(self, expected, closure=None):
        return self.len.greater_than(expected, closure)

    def has_keys(self, expected, closure=None):
        return self.len.greater_than(max(expected), closure)

    def has_any_key(self, expected, closure=None):
        return self.len.greater_than(min(expected), closure)

    def has_all(self, expected, closure=None):
        return self.should(ContainsAll, expected, closure)

    def has_any(self, expected, closure=None):
        return self.should(ContainsAny, expected, closure)

    def at(self, position):
        from .factory import DefaultMethodFactory
        closure = self.should.closure(lambda _list: _list[position])
        return DefaultMethodFactory(getter=closure)


class ListItemMethod(ListMethod):
    def __call__(self, expected):
        return self.has(expected)
