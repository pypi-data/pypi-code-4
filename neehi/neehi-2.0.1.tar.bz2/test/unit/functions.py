""" Tests for functions in the neehi package.

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


class TestFunctions(unittest.TestCase):

    def setUp(self):
        neehi._defaultproxy = None

    def test_setdefaultproxy(self):
        """ Set a default proxy. """
        self.assertIsNone(neehi._defaultproxy)

        neehi.setdefaultproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                                addr = '127.0.0.1',
                                port = 8080,
                                rdns = False,
                                username = 'testuser',
                                password = 'testpass'
                             )
        self.assertEqual(neehi._defaultproxy[0], neehi.PROXY_TYPE_SOCKS5)
        self.assertEqual(neehi._defaultproxy[1], '127.0.0.1')
        self.assertEqual(neehi._defaultproxy[2], 8080)
        self.assertEqual(neehi._defaultproxy[3], False)
        self.assertEqual(neehi._defaultproxy[4], 'testuser')
        self.assertEqual(neehi._defaultproxy[5], 'testpass')

        # check that the default proxy is used when a new socksocket is created
        sock = neehi.socksocket()
        self.assertEqual(sock._socksocket__proxy[0], neehi.PROXY_TYPE_SOCKS5)
        self.assertEqual(sock._socksocket__proxy[1], '127.0.0.1')
        self.assertEqual(sock._socksocket__proxy[2], 8080)
        self.assertEqual(sock._socksocket__proxy[3], False)
        self.assertEqual(sock._socksocket__proxy[4], 'testuser')
        self.assertEqual(sock._socksocket__proxy[5], 'testpass')

    def test_socks5(self):
        """ Create a SOCKS5-ready socksocket. """
        sock = neehi.socks5('127.0.0.1', 1080)
        self.assertTrue(isinstance(sock, neehi.socksocket))

    def test_socks4(self):
        """ Create a SOCKS4-ready socksocket. """
        sock = neehi.socks4('127.0.0.1', 1080)
        self.assertTrue(isinstance(sock, neehi.socksocket))

    def test_httpconn(self):
        """ Create an HTTP CONNECT-ready socksocket. """
        sock = neehi.httpconn('127.0.0.1', 1080)
        self.assertTrue(isinstance(sock, neehi.socksocket))

