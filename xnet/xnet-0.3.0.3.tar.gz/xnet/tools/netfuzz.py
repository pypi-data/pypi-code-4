#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['NetfuzzTool']


import socket
import urllib
import base64

from xnet.tools import Tool


def _tcp4_connect(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    return sock


class Template(object):

    _ESCAPE_SEQUENCES = (
        ('\\r', '\r'),
        ('\\n', '\n'),
    )

    def __init__(self, path, default_template):
        if path:
            f = open(path, 'rb')
            self._template = f.read()
            f.close()
        else:
            self._template = default_template
        self._slices = self._template.split('{}')
        self._nr_placeholders = len(self._slices) - 1

    def _unescape(self, result):
        result = result.decode('string-escape')
        for (es, ch) in self._ESCAPE_SEQUENCES:
            result = result.replace(es, ch)
        return result

    def sniper(self, payload, unescape=False):
        s = self._slices
        for i in xrange(1, len(s)):
            head = ''.join(s[:i])
            foot = ''.join(s[i:])
            result = head + payload + foot
            if unescape:
                result = self._unescape(result)
            yield result


class NetfuzzTool(Tool):
    '''
        NetfuzzTool
    '''

    __toolname__ = 'netfuzz'
    __itemname__ = 'host'
    __description__ = 'Send various payloads to target'

    cmdline_options = [
        ('-a', '--address', 'Target address, specified as host:port',
            dict(dest='address', metavar='addr')),
        ('-t', '--template', 'Template file containing {} placeholders where payloads are inserted',
            dict(dest='template', metavar='path')),
        ('', '--tag-lines', 'tag output lines with insertion point index and payload',
            dict(dest='tag_lines', action='store_true')),
        ('-u', '--urlenc', 'urlencode payloads',
            dict(dest='urlenc', action='store_true')),
        ('-b', '--base64', 'base64-encode payloads',
            dict(dest='base64', action='store_true')),
        ('-e', '--unescape', 'unescape in template and payload: \\r, \\n, \\xXX',
            dict(dest='unescape', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def _new_connection(self):
        return _tcp4_connect(self._addr)

    @classmethod
    def __setup__(cls, options):
        cls._template = Template(options.template, '{}')
        address = options.address
        assert ':' in address
        (host, port) = address.split(':')
        assert port.isdigit()
        cls._addr = (host, int(port))
        conn = _tcp4_connect(cls._addr)  # verify connectivity
        conn.close()

    #
    # NOTE! passing dict from __massage__() to __parse__()
    # in order to preserve payload info for instances.
    #
    @classmethod
    def __massage__(cls, iterator, options):
        for (pindex, payload) in enumerate(iterator):
            if payload[-1] == '\n':
                payload = payload[:-1]
            if options.apply:
                #
                # We handle --apply "manually" as __massage__() passes
                # dict to __parse__(). This makes the main class ignore
                # --apply silently.
                # Makes most sense to do this before base64 and urlenc.
                #
                payload = cls._apply(options.apply, payload)
            if options.base64:
                payload = base64.b64encode(payload)
            if options.urlenc:
                payload = urllib.quote(payload)
            it = cls._template.sniper(payload, options.unescape)
            for (inspoint, request) in enumerate(it):
                yield {
                    'request': request,
                    'payload': payload,
                    'pindex': pindex,
                    'inspoint': inspoint,
                }

    def __parse__(self, item, iterator):
        return item

    def __action__(self, parse_result):
        request = parse_result['request']
        result = parse_result.copy()
        conn = None
        #
        conn = self._new_connection()
        conn.send(request)
        response = conn.recv(65535)
        if response and self.options.tag_lines:
            tag = '{0},{1}:'.format(result['inspoint'], result['payload'])
            response = '\n' + tag + response.replace('\n', '\n' + tag)
        result['addr'] = '{0}:{1}'.format(*self._addr)
        result['host'] = self._addr[0]
        result['port'] = self._addr[1]
        result['response'] = response
        return result

    def __filter__(self, action_result):
        return action_result

    def __format__(self, line, parse_result, action_result):
        return action_result['response']

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 addr     - target address
 host     - target host
 port     - target port
 response - server response
 request  - client request
 payload  - payload
 pindex   - payload index
 inspoint - insertion point, starting from 0
 time     - time consumed by action, in ms
 pid      - PID of executing process
 grid     - Greenlet ID of executing process

Default format:
 '{response}'
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        if hasattr(self, '_addr'):
            return '{0}:{1} wait-timeout\n'.format(*self._addr)
        return None

    def __filename__(self):
        return 'pindex_{0}_inspoint_{1}'.format(
            self._action_result['pindex'],
            self._action_result['inspoint'],
        )


def main():
    import xnet.tools.run
    xnet.tools.run.run(NetfuzzTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
