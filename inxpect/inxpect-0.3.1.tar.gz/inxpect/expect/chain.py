# -*- coding: utf8 -*-
from . import pickle23

__all__ = ['OrChain', 'AndChain']

class Chain(list):
    fail = lambda self, at, *args, **kwargs: False
    success = lambda self, *args, **kwargs: True

    def __init__(self, *args):
        list.__init__(self, args)

    def on_fail(self, callback):
        if not callable(callback):
            callback = lambda self: callback
        self.fail = type(self.on_fail)(callback, self)

    def on_success(self, callback):
        if not callable(callback):
            callback = lambda self: callback
        self.success = type(self.on_success)(callback, self)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return pickle23.dumps(self)

class OrChain(Chain):
    def __call__(self, *args, **kwargs):
        for condition in self:
            if condition(*args, **kwargs) is True:
                return self.success(*args, **kwargs)
        return self.fail(condition, *args, **kwargs)

    def __or__(self, condition):
        if isinstance(condition, list):
            self.extend(condition)
        else:
            self.append(condition)
        return self

    def __and__(self, condition):
        return AndChain(self, condition)

    __ror__ = __or__
    __rand__ = __and__


class AndChain(Chain):
    def __call__(self, *args, **kwargs):
        for condition in self:
            if condition(*args, **kwargs) is False:
                return self.fail(condition, *args, **kwargs)
        return self.success(*args, **kwargs)

    def __or__(self, condition):
        return OrChain(self, condition)

    def __and__(self, condition):
        if isinstance(condition, list):
            self.extend(condition)
        else:
            self.append(condition)
        return self

    __ror__ = __or__
    __rand__ = __and__



