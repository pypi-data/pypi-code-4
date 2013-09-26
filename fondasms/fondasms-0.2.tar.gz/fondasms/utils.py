#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime


def import_path(callable_name, module, fallback):
    def do_import(name):
        ''' import a callable from full module.callable name '''
        modname, __, attr = name.rpartition('.')
        if not modname:
            # single module name
            return __import__(attr)
        m = __import__(modname, fromlist=[attr])
        return getattr(m, attr)

    ret = lambda mod, call: do_import('{module}.{callable}'.format(module=mod,
                                                                   callable=call))
    try:
        return ret(module, callable_name)
    except ImportError:
        return ret(fallback, callable_name)


def outgoing_for(to, message, ident=None, priority=0):
    outgoing = {'to': to,
                'message': message}
    if ident is not None:
        outgoing.update({'id': ident})
    if priority:
        outgoing.update({'priority': priority})
    return outgoing


def datetime_from_timestamp(timestamp):
    try:
        return datetime.datetime.fromtimestamp(int(timestamp) / 1000)
    except (TypeError, ValueError):
        return None
    return None
