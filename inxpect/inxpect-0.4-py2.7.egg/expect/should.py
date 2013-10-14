# -*- coding: utf8 -*-
from .operator import *
from .getters import FirstArg, GetterClosure

class Should(object):
    def __init__(self, getter, returns):
        if not callable(getter):
            getter = FirstArg()
        self.returns = returns
        self.closure = lambda find=None: GetterClosure(getter, find)

    def __get__(self, instance, ownerCls):
        return self

    def __call__(self, operator, expected, closure=None):
        if not issubclass(operator, Operator):
            operator = getattr(operators, operator, NullOperator)
        return self.returns(operator(expected, self.closure(closure)))

    def __eq__(self, expected):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(Equal, *expected)

    def __ne__(self, expected, closure=None):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(NotEqual, *expected)

    def __lt__(self, expected, closure=None):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(LowerThan, *expected)

    def __gt__(self, expected, closure=None):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(GreaterThan, *expected)

    def __le__(self, expected, closure=None):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(LowerOrEqualThan, *expected)

    def __ge__(self, expected, closure=None):
        if not isinstance(expected, tuple):
            expected = (expected, )

        return self(GreaterOrEqualThan, *expected)

class ShouldNot(Should):
    def __call__(self, operator, expected, closure=None):
        if not issubclass(operator, Operator):
            operator = getattr(operators, operator, NullOperator)
        operation = operator(expected, self.closure(closure))
        operation.deny = True
        return self.returns(operation)
