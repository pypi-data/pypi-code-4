""" Tests for the neehi package socksocket class.

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


class TestSockSocket(unittest.TestCase):

    def setUp(self):
        neehi._defaultproxy = None
        self.sock = neehi.socksocket()

    def tearDown(self):
        self.sock.close()
        del self.sock

    def test_setproxy(self):
        """ Set the proxy information. """
        for item in self.sock._socksocket__proxy:
            self.assertIsNone(item)

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = False,
                            username = 'testuser',
                            password = 'testpass'
                          )
        self.assertEqual(self.sock._socksocket__proxy[0], neehi.PROXY_TYPE_SOCKS5)
        self.assertEqual(self.sock._socksocket__proxy[1], '127.0.0.1')
        self.assertEqual(self.sock._socksocket__proxy[2], 8080)
        self.assertEqual(self.sock._socksocket__proxy[3], False)
        self.assertEqual(self.sock._socksocket__proxy[4], 'testuser')
        self.assertEqual(self.sock._socksocket__proxy[5], 'testpass')

    def test_recvall(self):
        """ Check __recvall. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   b'',
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.assertEqual(self.sock._socksocket__recvall(2), RESP5_AUTH_NONE)
        self.assertRaises(neehi.GeneralProxyError, self.sock._socksocket__recvall, 2)

    def test_connect_bad_input(self):
        """ Basic check of connect input. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                '192.168.1.1:80')
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                ('192.168.1.1:80'))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                (True, 80))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                ('192.168.1.1', '80'))

    def test_connect_default_sock5_port(self):
        """ Basic check of connect default SOCKS5 port. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                          )
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.sock.connect(('192.168.1.1', 80))

    def test_connect_default_sock4_port(self):
        """ Basic check of connect default SOCKS4 port. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                          )
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.sock.connect(('192.168.1.1', 80))

    def test_connect_default_http_port(self):
        """ Basic check of connect default HTTP port. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                          )
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.sock.connect(('192.168.1.1', 80))

    def test_connect_no_proxy(self):
        """ Connect without a proxy. """
        self.sock.connect(('192.168.1.1', 80))

    def test_connect_unknown_proxy_type(self):
        """ Connect with unknown proxy type. """
        self.sock.setproxy(proxytype = 'LATEST_GREATEST_PROTOCOL',
                            addr = '127.0.0.1',
                          )
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

    def test_socks5_no_auth(self):
        """ Connect without authentication. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )

        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock._socksocket__proxypeername,
                                                    ('192.168.1.1', 80))

    def test_socks5_auth(self):
        """ Connect with authentication. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_BASIC,
                                   RESP5_AUTHSTAT_SUCCESS,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            username = 'testuser',
                            password = 'testpass'
                          )

        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock._socksocket__proxypeername,
                                                    ('192.168.1.1', 80))

    def test_socks5_auth_fails(self):
        """ Fail authentication with username and password. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            username = 'testuser',
                            password = 'testpass'
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_BASIC,
                                   RESP5_AUTHSTAT_EBADMSG,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_BASIC,
                                   RESP5_AUTHSTAT_FAIL,
                                 ))
        self.assertRaises(neehi.Socks5AuthError, self.sock.connect,
                                                    ('192.168.1.1', 80))

    def test_socks5_fail_auth_methods(self):
        """ Fail to find an acceptable authentication method. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_EBADMSG,))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_EBADMSG2,))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NOTALLOWED,))
        self.assertRaises(neehi.Socks5AuthError, self.sock.connect,
                                                    ('192.168.1.1', 80))

    def test_socks5_request_connection_ip(self):
        """ Request the SOCKS5 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.sock.connect(('192.168.1.1', 80))

    def test_socks5_request_connection_remote_dns(self):
        """ Request the SOCKS5 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.sock.connect(('example.org', 80))

    def test_socks5_request_connection_local_dns(self):
        """ Request the SOCKS5 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = False
                          )

        socket.gethostbyname = mocks.gethostbyname('192.168.200.1')

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.sock.connect(('example.org', 80))

    def test_socks5_connection_fail(self):
        """ Request the SOCKS5 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_EBADMSG,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_FAILGEN,
                                 ))
        self.assertRaises(neehi.Socks5Error, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_UNKNOWN,
                                 ))
        self.assertRaises(neehi.Socks5Error, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_EBADMSG2,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

    def test_socks5_getproxysockname_fixed_addr(self):
        """ Get the SOCKS5 proxy's bound host information for a fixed-length address. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )
        self.assertEqual(self.sock.getproxysockname(), None)
        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock.getproxysockname(),
                                (socket.inet_aton('127.0.0.1'), 8080))

    def test_socks5_getproxysockname_variable_addr(self):
        """ Get the SOCKS5 proxy's bound host information for a variable-length address. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRVAR,
                                   b'\x04',
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))
        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock.getproxysockname(),
                                (socket.inet_aton('127.0.0.1'), 8080))

    def test_socks5_getproxypeername(self):
        """ Get the name of the SOCKS5 proxy. """
        self.sock.set_address(('127.0.0.1', 8080))
        self.assertEqual(self.sock.getproxypeername(), ('127.0.0.1', 8080))

    def test_socks5_getpeername(self):
        """ Get the peer name from the SOCKS5 proxy. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP5_AUTH_NONE,
                                   RESP5_REQCONN_ADDRFIX,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS5,
                            addr = '127.0.0.1',
                            port = 8080,
                          )
        self.assertEqual(self.sock.getpeername(), None)
        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock.getpeername(), ('192.168.1.1', 80))

    def test_socks4_request_connection_remote_dns(self):
        """ Request the SOCKS4 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.sock.connect(('example.org', 80))

    def test_socks4_request_connection_local_dns(self):
        """ Request the SOCKS4 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = False
                          )

        socket.gethostbyname = mocks.gethostbyname('192.168.200.1')

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.sock.connect(('example.org', 80))

    def test_socks4_request_connection_with_username(self):
        """ Request the SOCKS4 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True,
                            username = 'testuser',
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.sock.connect(('192.168.1.1', 80))

    def test_socks4_connection_fail(self):
        """ Request the SOCKS4 proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_EBADMSG,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_REJECT,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.assertRaises(neehi.Socks4Error, self.sock.connect,
                                                    ('192.168.1.1', 80))

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_UNKNOWN,
                                   RESP4_EMPTY_ADDR,
                                 ))
        self.assertRaises(neehi.Socks4Error, self.sock.connect,
                                                    ('192.168.1.1', 80))

    def test_socks4_getproxysockname(self):
        """ Get the SOCKS4 proxy's bound host information. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   b'\x1F\x90',                     # bound port number
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                          )
        self.assertEqual(self.sock.getproxysockname(), None)
        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock.getproxysockname(),
                                ('127.0.0.1', 8080))

    def test_socks4_getpeername(self):
        """ Get the peer name from the SOCKS4 proxy. """
        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESP4_REQCONN_SUCCESS,
                                   socket.inet_aton('127.0.0.1'),   # bound address
                                   b'\x1F\x90',                     # bound port number
                                 ))

        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_SOCKS4,
                            addr = '127.0.0.1',
                            port = 8080,
                          )
        self.assertEqual(self.sock.getpeername(), None)
        self.sock.connect(('192.168.1.1', 80))
        self.assertEqual(self.sock.getpeername(), ('192.168.1.1', 80))

    def test_http_request_connection_remote_dns(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.sock.connect(('example.org', 80))

    def test_http_request_connection_local_dns(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = False
                          )

        socket.gethostbyname = mocks.gethostbyname('192.168.200.1')

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.sock.connect(('example.org', 80))

    def test_http_request_connection_http_11(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER11,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.sock.connect(('example.org', 80))

    def test_http_request_connection_bad_http_version(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VERBAD,
                                   RESPHTTP_STATUS_200,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('example.org', 80))

    def test_http_request_connection_invalid_status(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_INVALID,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.assertRaises(neehi.GeneralProxyError, self.sock.connect,
                                                    ('example.org', 80))

    def test_http_request_connection_404(self):
        """ Request the HTTP proxy open a connection to the endpoint. """
        self.sock.setproxy(proxytype = neehi.PROXY_TYPE_HTTP,
                            addr = '127.0.0.1',
                            port = 8080,
                            rdns = True
                          )

        # set the responses we want to receive from the "SOCKS proxy"
        self.sock.load_recv_deque((RESPHTTP_VER10,
                                   RESPHTTP_STATUS_404,
                                   RESPHTTP_EOL,
                                   RESPHTTP_MSGEND,
                                 ))
        self.assertRaises(neehi.HTTPError, self.sock.connect,
                                                    ('example.org', 80))

