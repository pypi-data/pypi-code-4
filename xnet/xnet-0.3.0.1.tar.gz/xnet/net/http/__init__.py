#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

import unittest
import urlparse
import sys
import os
import re

from xnet.net.ipv4 import AddressIterator
from xnet.net.ipv4 import PortRangeIterator

try:
    import lxml.etree
except ImportError:
    import time
    errmsg = '\n'
    errmsg += '*** XNET USAGE INFORMATION ***\n'
    errmsg += '\n'
    errmsg += 'ImportError raised, lxml.etree might be missing.\n'
    errmsg += 'For Debian, try:\n'
    errmsg += '  $ sudo apt-get install python-lxml\n'
    errmsg += 'For OSX, try:\n'
    errmsg += '  $ sudo port install py-lxml\n'
    print errmsg
    time.sleep(3)
    raise

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


class HTMLParser(object):

    def __init__(self, body_unicode):
        htmlparser = lxml.etree.HTMLParser()
        self._body_unicode = self._prepare_body(body_unicode)
        #
        # Try/catch to fix remaining lxml exceptions.
        #
        try:
            self._tree = lxml.etree.fromstring(self._body_unicode, htmlparser)
        except:
            print body_unicode
            raise

    def _prepare_body(self, body_unicode):
        #
        # Hairy fix to remove encoding='..' from xml headers, as
        # lxml doesn't accept these.
        #
        m = re.match(r'''(?i)<\?xml[\s\w'=.]+(encoding=['"][^'"]*['"])''', body_unicode)
        if m:
            body_unicode = ''.join(body_unicode.split(m.group(1)))
        return body_unicode

    def xpath(self, xpath, match_delimiter='\n', strict=False):
        xpath_result = self._tree.xpath(xpath)
        success = False
        output = ''
        for elem in xpath_result:
            success = True
            if type(elem) is lxml.etree._ElementStringResult:
                elem = str(elem)
            if not type(elem) is str:
                if isinstance(elem, lxml.etree._ElementUnicodeResult):
                    elem = unicode(elem)
                    elem = elem.encode('utf-8', 'replace')
                else:
                    elem = lxml.etree.tostring(elem)
            if len(output):
                output += match_delimiter
            output += elem
        if strict and not success:
            import tempfile
            (fd, name) = tempfile.mkstemp(prefix='xpath-fail-')
            os.write(fd, self._body_unicode.encode('utf-8'))
            os.close(fd)
            msg = 'Error: XPath not matched: {0}'.format(xpath)
            msg += ', body saved to {0}'.format(name)
            sys.exit(msg)
        return output


def _test():
    import doctest
    import unittest
    print('doctest: ' + doctest.testmod().__str__())
    unittest.main()

if __name__ == "__main__":
    _test()
