# -*- coding: utf8 -*-
from .getters import FirstArg, AnonymousFunc, _getter_
from . import pickle23

__all__ = [
    'Equal', 'NotEqual', 'SameAs', 'NotSameAs',
    'LowerThan', 'LowerOrEqualThan', 'GreaterThan', 'GreaterOrEqualThan',
    'Contains', 'NotContains', 'ContainsAll', 'ContainsAny',
    'ContainsItem', 'ContainsAllItem', 'ContainsAnyItem',
    'ContainsValue', 'ContainsAllValue', 'ContainsAnyValue',
    'InstanceOf', 'NotInstanceOf', 'TypeIs', 'TypeIsNot'
]

class __Operator(object):
    def __init__(self, expected, getter=None):
        self.expected = expected
        if not callable(getter):
            getter = FirstArg()
        elif not isinstance(getter, _getter_):
            getter = AnonymousFunc(getter)
        self.getter = getter

    def __call__(self, *args, **kwargs):
        return self.is_true(self.getter(*args, **kwargs), self.expected)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return pickle23.dumps(self)

    @classmethod
    def is_false(cls, given, expected):
        return not cls.is_true(given, expected)

class Equal(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given == expected

class NotEqual(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return Equal.is_false(given, expected)

class SameAs(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given is expected

class NotSameAs(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return SameAs.is_false(given, expected)

class LowerThan(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given < expected

class LowerOrEqualThan(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given <= expected

class GreaterThan(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given > expected

class GreaterOrEqualThan(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return given >= expected

class TypeIs(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return type(given) is expected

class TypeIsNot(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return TypeIs.is_false(given, expected)

class InstanceOf(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return isinstance(given, expected)

class NotInstanceOf(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return InstanceOf.is_false(given, expected)

class Contains(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return expected in given

class NotContains(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        return Contains.is_false(given, expected)

class ContainsAny(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in expected:
            if Contains.is_true(given, value):
                return True
        return False

class ContainsAll(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in expected:
            if Contains.is_false(given, value):
                return False
        return True

class ContainsItem(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        name, value = expected
        if Contains.is_true(given.keys(), name) and Equal.is_true(value, given.get(name)):
            return True
        return False

class ContainsAnyItem(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for item in expected.items():
            if ContainsItem.is_true(given, item):
                return True
        return False

class ContainsAllItem(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for item in expected.items():
            if ContainsItem.is_false(given, item):
                return False
        return True


class ContainsValue(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Equal.is_true(value, expected):
                return True
        return False

class ContainsAllValue(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Contains.is_false(expected, value):
                return False
        return True

class ContainsAnyValue(__Operator):
    @classmethod
    def is_true(cls, given, expected):
        for value in given.values():
            if Contains.is_true(expected, value):
                return True
        return False
