# -*- coding: utf8 -*-
from .chain import AndChain
from .getters import FirstArg, ObjectLen
from . import operator


class DefaultProperty(object):
    returns = AndChain
    def __init__(self, _getter_=None):
        if not callable(_getter_):
            _getter_ = FirstArg(_getter_)
        self.get_finder = lambda find=_getter_: callable(find) and find or _getter_

    def _functor(self, operator, expected, _getter_=None):
        find = self.get_finder(_getter_)
        return self.returns(operator(expected, find))

    def equal_to(self, expected, _getter_=None):
        return self._functor(operator.Equal, expected, _getter_)

    def not_equal_to(self, expected, _getter_=None):
        return self._functor(operator.NotEqual, expected, _getter_)

    def lower_than(self, expected, _getter_=None):
        return self._functor(operator.LowerThan, expected, _getter_)

    def lower_or_equal_than(self, expected, _getter_=None):
        return self._functor(operator.LowerOrEqualThan, expected, _getter_)

    def greater_than(self, expected, _getter_=None):
        return self._functor(operator.GreaterThan, expected, _getter_)

    def greater_or_equal_than(self, expected, _getter_=None):
        return self._functor(operator.GreaterOrEqualThan, expected, _getter_)

    def same_as(self, expected, _getter_=None):
        return self._functor(operator.SameAs, expected, _getter_)

    def not_same_as(self, expected, _getter_=None):
        return self._functor(operator.NotSameAs, expected, _getter_)

    def type_is(self, expected, _getter_=None):
        return self._functor(operator.TypeIs, expected, _getter_)

    def type_is_not(self, expected, _getter_=None):
        return self._functor(operator.TypeIsNot, expected, _getter_)

    def instance_of(self, expected, _getter_=None):
        return self._functor(operator.InstanceOf, expected, _getter_)

    def not_instance_of(self, expected, _getter_=None):
        return self._functor(operator.NotInstanceOf, expected, _getter_)

    @property
    def len(self):
        _getter_ = self.get_finder()
        return DefaultProperty(_getter_=ObjectLen(_getter_))

    def __get__(self, instance, ownerCls):
        return self

    __eq__ = equal_to
    __ne__ = not_equal_to
    __lt__ = lower_than
    __gt__ = greater_than
    __le__ = lower_or_equal_than
    __ge__ = greater_or_equal_than

