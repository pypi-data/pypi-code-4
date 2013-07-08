#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

import unittest
import urlparse

from xnet.net.ipv4 import AddressIterator
from xnet.net.ipv4 import PortRangeIterator


class UrlIteratorException(Exception):
    pass


class UrlIterator:
    '''
        #>>> ui = lambda s: list(UrlIterator().expand(s))
    '''

    _E_INVALID_PROTOCOL = 'Unknown protocol: {0}'

    def __init__(self, default_scheme='http', default_ports=None):
        '''
            default_ports - iterable or str-type port range
        '''
        self._default_scheme = default_scheme
        if type(default_ports) is str:
            default_ports = list(PortRangeIterator(default_ports))
        self._default_ports = default_ports

    def _remove_redundant_port(self, url):
        '''
            Remove :80 from http:// and :443 from https:// urls.
        '''
        u = urlparse.urlparse(url)
        if ':' in u.netloc:
            (host, port) = u.netloc.rsplit(':', 1)
            if u.scheme == 'http' and port == '80' or u.scheme == 'https' and port == '443':
                return urlparse.urlunsplit((
                    u.scheme, host, u.path, u.query, u.fragment
                ))
        return url

    def expand(self, xurl):
        xurl = str(xurl).strip()
        scheme = self._default_scheme
        default_ports = self._default_ports
        if '://' in xurl:
            scheme, xurl = xurl.split('://', 1)
            if scheme == 'http':
                default_ports = [80]
            elif scheme == 'https':
                default_ports = [443]
            else:
                raise UrlIteratorException(self._E_INVALID_PROTOCOL.format(scheme))

        if not '/' in xurl:
            xurl += '/'
        (xaddr, path) = xurl.split('/', 1)
        path = '/' + path

        addressIterator = AddressIterator(default_ports=default_ports,
                                          allow_netmasks=False)

        for addr in addressIterator.expand(xaddr):
            url = scheme + '://' + addr + path
            url = self._remove_redundant_port(url)
            yield url


class Test_UrlIterator(unittest.TestCase):
    def test1(self):
        ui = lambda xurl: list(UrlIterator(default_scheme='http', default_ports=[33]).expand(xurl))
        #
        # use default_ports
        #
        self.assertEqual(
            ui('10.0.0.1'),
            [
                'http://10.0.0.1:33/'
            ]
        )
        #
        # http-scheme overrides default_ports
        #
        self.assertEqual(
            ui('http://10.0.0.1'),
            [
                'http://10.0.0.1/'
            ]
        )
        #
        # https-scheme overrides default_ports
        #
        self.assertEqual(
            ui('https://10.0.0.1'),
            [
                'https://10.0.0.1/'
            ]
        )
        #
        # https-scheme overrides default_ports
        #
        self.assertRaises(
            UrlIteratorException,
            ui,
            'foo://10.0.0.1'
        )
        #
        # permutations
        #
        self.assertEqual(
            ui('http://10.0.1-2.3-4:5,6/index.html'),
            [
                'http://10.0.1.3:5/index.html',
                'http://10.0.1.3:6/index.html',
                'http://10.0.1.4:5/index.html',
                'http://10.0.1.4:6/index.html',
                'http://10.0.2.3:5/index.html',
                'http://10.0.2.3:6/index.html',
                'http://10.0.2.4:5/index.html',
                'http://10.0.2.4:6/index.html',
            ]
        )


def _test():
    import doctest
    import unittest
    print('doctest: ' + doctest.testmod().__str__())
    unittest.main()

if __name__ == "__main__":
    _test()
