#!/usr/bin/env python
# coding=utf-8

"""utility functions

"""


def ok(**kwargs):
    """return kwargs as a dict with key 'ok' being True."""
    kwargs["ok"] = True
    return kwargs


def error(**kwargs):
    """return kwargs as a dict with key 'ok' being False."""
    kwargs["ok"] = False
    return kwargs


def fargs(args):
    """format a args tuple to unicode string.

    """
    return u', '.join(unicode(arg) for arg in args)


def count_if(func, lst):
    """count how many obj in lst that cause func(obj) eval to truth value.

    Args:
        func: any callable
        lst: any iterable

    """
    try:
        values = (func(obj) for obj in lst)
    except TypeError as e:
        raise TypeError(u'Bad param for count_if', *e.args)
    truth_values = [v for v in values if v]
    count = len(truth_values)
    return count
