#-*- coding: utf8 -*-
from . import pickle23
from jsonpickle import handlers


class _getter_(object):
    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return pickle23.dumps(self)

class AnonymousFunc(_getter_):
    def __init__(self, func):
        if not hasattr(func, '__code__'):
            self.func = lambda *args, **kwargs: func(*args, **kwargs)
        else:
            self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __reduce__(self):
        # Use only for comparisons
        co = self.func.__code__
        return LambdaCode, (co.co_argcount, 0, 0, 0, co.co_code, co.co_consts, co.co_names,
            co.co_varnames, __file__, co.co_name, 0, 0)


class LambdaCode(AnonymousFunc):
    def __init__(self, *code_args):
        import types
        code = types.CodeType(*code_args)
        AnonymousFunc.__init__(types.LambdaType(code, globals()))


class GetterClosure(_getter_):
    def __init__(self, getter, closure=None):
        if not callable(closure):
            closure = FirstArg()
        if not isinstance(closure, _getter_):
            closure = AnonymousFunc(closure)
        self.closure = closure
        self.getter = getter

    def __call__(self, *args, **kwargs):
        return self.closure(self.getter(*args, **kwargs))

class AsIs(_getter_):
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value

class FirstArg(_getter_):
    def __call__(self, *args, **kwargs):
        return args[0]

class AttrByName(_getter_):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __call__(self, instance, default=None):
        return getattr(instance, self.attr_name, default)


handlers.register(AnonymousFunc, handlers.SimpleReduceHandler)
