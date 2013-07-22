import functools
import re

from flask import request


def _parse_rule(s):
    return re.match("\<(?:(string|float|int):)?([a-zA-Z_]\w*)\>", s).groups()


CONVERTORS = {'string': str, 'float': float, 'int': int}


def _make_schema(rule):
    schema = []
    for item in rule.split():
        kind, name = _parse_rule(item)
        schema.append((name, CONVERTORS[kind or 'string']))
    return schema


def _make_decorator(rule, dictname):
    schema = _make_schema(rule)

    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwds):
            argsdict = getattr(request, dictname)
            for name, convertor in schema:
                kwds[name] = convertor(argsdict[name])
            return f(*args, **kwds)
        return decorated
    return decorator


def form_args(rule):
    return _make_decorator(rule, 'form')


def query_args(rule):
    return _make_decorator(rule, 'args')


def value_args(rule):
    return _make_decorator(rule, 'values')
