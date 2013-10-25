# -*- coding: utf-8 -*-

import logging
import inspect
import socket
import struct
from inspect import getmembers, ismethod


def autolog(message=None, level=logging.DEBUG):
    func = inspect.currentframe().f_back.f_code
    frame = inspect.stack()[1]
    values = inspect.formatargvalues(*inspect.getargvalues(frame[0]))
    module = inspect.getmodule(frame[0])
    logger = logging.getLogger(module.__name__)
    logger.log(level, '%s [%s] : %s' % (func.co_name, values, message))


def enum(**enums):
    return type('Enum', (), dict(enums.items() + {'items': enums}.items()))


def ip2long(ip):
    packed = socket.inet_aton(ip)
    return long(struct.unpack('!L', packed)[0])


def long2ip(lg):
    return socket.inet_ntoa(struct.pack('!L', lg))


def to_dict(o, limit=()):
    m = getmembers(o, lambda x: not ismethod(x))
    m = [i for i in m if not i[0].startswith('_')]
    if limit:
        m = [i for i in m if i[0] in limit]
    return dict(m)


def walk(value, graph_max=None, graph_interface=None,
         _graph_path=[], _graph_current=0):

    def _recur(v):
        return walk(v, graph_max=graph_max, graph_interface=graph_interface,
                    _graph_path=_graph_path, _graph_current=_graph_current)

    if graph_interface and isinstance(value, graph_interface):
        if graph_max and _graph_current >= graph_max:
            return 'REC_MAX'

        if _graph_path:
            if len(_graph_path) >= 2 and value is _graph_path[-2]:
                return 'REC_MAX'
            elif value in _graph_path:
                return walk(
                    to_dict(value), graph_max=1,
                    graph_interface=graph_interface,
                    _graph_path=[])

        _graph_path.append(value)
        _graph_current = _graph_current + 1

        value = to_dict(value)

    if type(value) is dict:
        d = {}
        for k, v in value.iteritems():
            r = _recur(v)
            if r == 'REC_MAX':
                continue
            d[k] = r
        return d

    if hasattr(value, '__iter__'):
        l = []
        for v in value:
            r = _recur(v)
            if r == 'REC_MAX':
                continue
            l.append(r)
        return l

    return value
