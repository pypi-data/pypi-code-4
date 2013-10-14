# -*- coding: utf8 -*-
from .chain import AndChain
from .operator import *
from .should import Should, ShouldNot


class DefaultProperty(object):
    def __init__(self, getter=None, returns=AndChain):
        self.should = Should(getter, returns)
        self.should_not = ShouldNot(getter, returns)

    def equal_to(self, expected, closure=None):
        return self.should(Equal, expected, closure)

    def not_equal_to(self, expected, closure=None):
        return self.should_not(Equal, expected, closure)

    def lower_than(self, expected, closure=None):
        return self.should(LowerThan, expected, closure)

    def lower_or_equal_than(self, expected, closure=None):
        return self.should(LowerOrEqualThan, expected, closure)

    def greater_than(self, expected, closure=None):
        return self.should(GreaterThan, expected, closure)

    def greater_or_equal_than(self, expected, closure=None):
        return self.should(GreaterOrEqualThan, expected, closure)

    def same_as(self, expected, closure=None):
        return self.should(SameAs, expected, closure)

    def not_same_as(self, expected, closure=None):
        return self.should_not(SameAs, expected, closure)

    def type_is(self, expected, closure=None):
        return self.should(TypeIs, expected, closure)

    def type_is_not(self, expected, closure=None):
        return self.should_not(TypeIs, expected, closure)

    def instance_of(self, expected, closure=None):
        return self.should(InstanceOf, expected, closure)

    def not_instance_of(self, expected, closure=None):
        return self.should_not(InstanceOf, expected, closure)

    @property
    def len(self):
        return DefaultProperty(getter=self.should.closure(len))

    def __get__(self, instance, ownerCls):
        return self

    __eq__ = equal_to
    __ne__ = not_equal_to
    __lt__ = lower_than
    __gt__ = greater_than
    __le__ = lower_or_equal_than
    __ge__ = greater_or_equal_than

