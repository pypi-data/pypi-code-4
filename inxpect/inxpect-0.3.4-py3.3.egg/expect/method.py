# -*- coding: utf8 -*-
from .property import DefaultProperty


class DefaultMethod(DefaultProperty):
    def __call__(self, expected):
        return self.equal_to(expected)


class SameMethod(DefaultMethod):
    def __call__(self, expected):
        return self.same_as(expected)

