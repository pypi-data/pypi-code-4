#!/usr/bin/env python3
"""
TEST.IO.TEST_API.PY -- test script for sub-package IO of package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests checking details of the external API for
the I/O modules in the PLIB3.IO sub-package.
"""

import unittest

from .testlib import IOChannelTest
from .testlib_async import AsyncHandler, AsyncServer
from .testlib_async import SocketClient as _AsyncClient
from .testlib_blocking import BlockingHandler, BlockingServer
from .testlib_blocking import SocketClient as _BlockingClient


class RestartMixin(object):
    
    restarted = False
    result = b""
    
    def client_communicate(self, data, client_id=None, callback=None):
        self.restarted = False
        self.result = b""
        super(RestartMixin, self).client_communicate(data,
                                                     client_id,
                                                     callback)
    
    def process_data(self):
        if self.restarted:
            self.result = self.read_data
        else:
            self.start(self.read_data)
            self.restarted = True


class AsyncClient(RestartMixin, _AsyncClient):
    pass


class AsyncTestMixin(IOChannelTest):
    
    client_class = AsyncClient
    handler_class = AsyncHandler
    server_class = AsyncServer


class BlockingClient(RestartMixin, _BlockingClient):
    pass


class BlockingTestMixin(IOChannelTest):
    
    client_class = BlockingClient
    handler_class = BlockingHandler
    server_class = BlockingServer


class APIMixin(object):
    
    test_data = b"Python rocks!"
    
    def get_client(self):
        client = self.client_class()
        client.setup_client(('localhost', self.server_port))
        return client
    
    def do_client_comm(self, client):
        client.client_communicate(self.test_data)
        self.assertTrue(client.restarted)
        self.assertEqual(client.result, self.test_data)


class RestartTestMixin(APIMixin):
    
    def test_restart(self):
        # Test that calling ``start`` inside the communication
        # loop keeps it open, even if ``keep_alive`` is false
        # on the client side; but once there is no more data,
        # the client closes.
        client = self.get_client()
        self.do_client_comm(client)
        self.assertTrue(client.closed)


class BlockingRestartTest(RestartTestMixin, BlockingTestMixin, unittest.TestCase):
    pass


class AsyncRestartTest(RestartTestMixin, AsyncTestMixin, unittest.TestCase):
    pass


class KeepAliveTestMixin(APIMixin):
    
    tries = 2
    
    def test_restart_keepalive(self):
        # Test that a client with ``keep_alive`` true can be
        # restarted without re-connecting, as long as finish
        # has not been called from user code (note that there
        # is no such call in the ``process_data`` method of
        # the client).
        client = self.get_client()
        client.keep_alive = True
        for _ in range(self.tries):
            self.do_client_comm(client)
        self.assertTrue(not client.closed)
        client.close()
        self.assertTrue(client.closed)


class BlockingKeepAliveTest(KeepAliveTestMixin, BlockingTestMixin, unittest.TestCase):
    pass


class AsyncKeepAliveTest(KeepAliveTestMixin, AsyncTestMixin, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
