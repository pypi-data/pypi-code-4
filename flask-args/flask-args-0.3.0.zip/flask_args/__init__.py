import functools

from flask import request


def _make_decorator(schema, dictname):

    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwds):
            argsdict = getattr(request, dictname)
            for name, convertor in schema.items():
                kwds[name] = convertor(argsdict[name])
            return f(*args, **kwds)
        return decorated
    return decorator


def args(source, **kwds):
    return _make_decorator(kwds, source)
