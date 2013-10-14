# -*- coding: utf8 -*-
from .getters import FirstArg, AnonymousFunc, _getter_
from . import pickle23

__all__ = [
    'Equal', 'NotEqual', 'SameAs', 'NotSameAs',
    'LowerThan', 'LowerOrEqualThan', 'GreaterThan', 'GreaterOrEqualThan',
    'Contains', 'NotContains', 'ContainsAll', 'ContainsAny',
    'ContainsItem', 'ContainsAllItem', 'ContainsAnyItem',
    'ContainsValue', 'ContainsAllValue', 'ContainsAnyValue',
    'InstanceOf', 'NotInstanceOf', 'TypeIs', 'TypeIsNot', 'Operator'
]

class Operator(object):
    deny = False
    def __init__(self, expected, getter=None):
        self.expected = expected
        if not callable(getter):
            getter = FirstArg()
        elif not isinstance(getter, _getter_):
            getter = AnonymousFunc(getter)
        self.getter = getter

    def __call__(self, *args, **kwargs):
        call = self.deny and self.is_false or self.is_true
        return call(self.getter(*args, **kwargs), self.expected)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return pickle23.dumps(self)

    @classmethod
    def is_false(cls, given, expected):
        return not cls.is_true(given, expected)

class NullOperator(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return True

class Equal(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given == expected

class NotEqual(Equal):
    deny = True

class SameAs(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given is expected

class NotSameAs(SameAs):
    deny = True

class LowerThan(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given < expected

class LowerOrEqualThan(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given <= expected

class GreaterThan(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given > expected

class GreaterOrEqualThan(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given >= expected

class TypeIs(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return type(given) is expected

class TypeIsNot(TypeIs):
    deny = True

class InstanceOf(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return isinstance(given, expected)

class NotInstanceOf(InstanceOf):
    deny = True

class Contains(Operator):
    @classmethod
    def is_true(cls, given, expected):
        return expected in given

class NotContains(Contains):
    deny = True

class ContainsAny(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in expected:
            if Contains.is_true(given, value):
                return True
        return False

class ContainsAll(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in expected:
            if Contains.is_false(given, value):
                return False
        return True

class ContainsItem(Operator):
    @classmethod
    def is_true(cls, given, expected):
        name, value = expected
        if Contains.is_true(given.keys(), name) and Equal.is_true(value, given.get(name)):
            return True
        return False

class ContainsAnyItem(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for item in expected.items():
            if ContainsItem.is_true(given, item):
                return True
        return False

class ContainsAllItem(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for item in expected.items():
            if ContainsItem.is_false(given, item):
                return False
        return True


class ContainsValue(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Equal.is_true(value, expected):
                return True
        return False

class ContainsAllValue(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Contains.is_false(expected, value):
                return False
        return True

class ContainsAnyValue(Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Contains.is_true(expected, value):
                return True
        return False
