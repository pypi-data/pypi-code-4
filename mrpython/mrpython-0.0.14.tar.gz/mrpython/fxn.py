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


def uberenum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    by_value = dict((value, key) for key, value in enums.iteritems())
    enums['by_value'] = by_value
    return type('Enum', (), enums)


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


def walk(
    value, graph_max=None, graph_interface=None, limit_check='_dict_attrs',
        _graph_path=[], _graph_current=0, _debug=False):

    if _debug:
        print '-----------'
        print 'V: %s' % (value)
        print 'GM: %s' % (graph_max)
        print 'GP: %s' % (_graph_path)
        print 'GC: %s' % (_graph_current)
        print '-----------'
        raw_input('s >')

    def _recur(v):
        return walk(v, graph_max=graph_max, graph_interface=graph_interface,
                    limit_check=limit_check, _graph_path=_graph_path,
                    _graph_current=_graph_current, _debug=_debug)

    def _to_dict(v):
        if limit_check:
            limits = getattr(v, limit_check, ())
            return to_dict(value, limit=limits)
        return to_dict(v)

    if graph_interface and isinstance(value, graph_interface):
        if graph_max and _graph_current >= graph_max:
            return 'REC_MAX'

        if _graph_path:
            if len(_graph_path) >= 2 and value is _graph_path[-2]:
                return 'REC_MAX'
            elif value in _graph_path:
                return walk(
                    _to_dict(value), graph_max=1,
                    graph_interface=graph_interface,
                    _graph_path=[])

        _graph_path.append(value)
        _graph_current = _graph_current + 1

        value = _to_dict(value)

    if type(value) is dict:
        d = {}
        for k, v in value.iteritems():
            r = _recur(v)
            if r == 'REC_MAX':
                continue
            d[k] = r
        return d

    '''
    list_type = False
    list_types = (
        list,
        set,
        tuple
    )

    for l in list_types:
        if isinstance(value, l):
            list_type = True
            break
    '''
    list_type = False
    try:
        iter(value)
        if not isinstance(value, basestring):
            list_type = True
    except TypeError:
        pass

    if list_type:
        l = []
        for v in value:
            r = _recur(v)
            if r == 'REC_MAX':
                continue
            l.append(r)
        return l

    return value
