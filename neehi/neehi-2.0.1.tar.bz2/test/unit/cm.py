""" Tests for the neehi.cm module.

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

socket.socket = mocks.MockSocket
import neehi
from neehi.cm import SocksProxy5, SocksProxy4, HttpProxy


class TestContextManagers(unittest.TestCase):

    def setUp(self):
        neehi.setdefaultproxy(None, None, None, None, None, None)
        self.sock = neehi.socksocket()

    def tearDown(self):
        self.sock.close()
        del self.sock

    def test_socksproxy5(self):
        """ Use a SOCKS5 proxy in context. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        with SocksProxy5('127.0.0.1', 8080):
            self.sock.connect(('example.org', 80))

    def test_socksproxy4(self):
        """ Use a SOCKS4 proxy in context. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   RESP4_EMPTY_ADDR,
                                 ))
        with SocksProxy4('127.0.0.1', 8080):
            self.sock.connect(('example.org', 80))

    def test_httpproxy(self):
        """ Use a HTTP CONNECT proxy in context. """
        # set the responses we want to receive from the "HTTP proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        with HttpProxy('127.0.0.1', 8080):
            self.sock.connect(('example.org', 80))

