""" Tests for the neehi package exception classes.

Copyright 2012 Sean Robinson <seankrobinson@gmail.com>

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the author nor the names of contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import socket
import unittest

from test import mocks
from test.unit import *

import neehi


class TestExceptions(unittest.TestCase):

    def raise_it(self, e, *args):
        """ Raise e. """
        raise e(*args)

    def test_proxyerror(self):
        """ ProxyError """
        self.assertRaises(neehi.ProxyError, self.raise_it,
                                        neehi.ProxyError, 'proxy error')
        self.assertEqual(str(neehi.ProxyError('proxy error')),
                                                            'proxy error')

    def test_generalproxyerror(self):
        """ GeneralProxyError """
        self.assertRaises(neehi.GeneralProxyError, self.raise_it,
                                            neehi.GeneralProxyError, 1)
        self.assertEqual(str(neehi.GeneralProxyError(1)),
                                                    '[1] Invalid data')

    def test_socks5autherror(self):
        """ Socks5AuthError """
        self.assertRaises(neehi.Socks5AuthError, self.raise_it,
                                                neehi.Socks5AuthError, 1)
        self.assertEqual(str(neehi.Socks5AuthError(1)),
                                            '[1] Authentication required')

    def test_socks5error(self):
        """ Socks5Error """
        self.assertRaises(neehi.Socks5Error, self.raise_it,
                                                    neehi.Socks5Error, 1)
        self.assertEqual(str(neehi.Socks5Error(1)),
                                        '[1] General SOCKS server failure')

    def test_socks4error(self):
        """ Socks4Error """
        self.assertRaises(neehi.Socks4Error, self.raise_it,
                                                    neehi.Socks4Error, 1)
        self.assertEqual(str(neehi.Socks4Error(1)),
                                        '[91] Request rejected or failed')

    def test_httperror(self):
        """ HTTPError """
        self.assertRaises(neehi.HTTPError, self.raise_it,
                                            neehi.HTTPError, 'HTTP error')
        self.assertEqual(str(neehi.HTTPError('HTTP error')), 'HTTP error')

