#!/usr/bin/env python3
"""
TEST.IO.TESTLIB_BLOCKING.PY -- utility module for PLIB3 I/O tests
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the tests of the blocking
I/O modules in PLIB3.IO.
"""

import sys

from plib.io.mixins import EchoRequestMixin

import plib.io.blocking  # FIXME: why is this needed to make things work?

from plib.io.blocking import (
    SocketClient, BaseRequestHandler, SocketServer,
    SocketClientWithShutdown, BaseRequestHandlerWithShutdown,
    SocketClientWithTerminator, BaseRequestHandlerWithTerminator,
    SocketClientWithReadWrite, BaseRequestHandlerWithReadWrite,
    ThreadingServer as _ThreadingServer
)

if sys.platform != 'win32':
    # The forking server currently does not work on Windows
    from plib.io.blocking import ForkingServer as _ForkingServer

from .testlib import IOClientMixin, IOServerMixin


class BlockingClient(IOClientMixin, SocketClient):
    pass


class BlockingHandler(EchoRequestMixin, BaseRequestHandler):
    pass


class BlockingServer(IOServerMixin, SocketServer):
    pass


if sys.platform != 'win32':
    
    class ForkingServer(IOServerMixin, _ForkingServer):
        pass


class ThreadingServer(IOServerMixin, _ThreadingServer):
    pass


class BlockingTestMixin(object):
    
    client_class = BlockingClient
    handler_class = BlockingHandler
    server_class = BlockingServer


class BlockingShutdownClient(IOClientMixin,
                             SocketClientWithShutdown):
    pass


class BlockingShutdownHandler(EchoRequestMixin,
                              BaseRequestHandlerWithShutdown):
    pass


class BlockingShutdownTestMixin(object):
    
    client_class = BlockingShutdownClient
    handler_class = BlockingShutdownHandler
    server_class = BlockingServer


class BlockingTerminatorClient(IOClientMixin,
                               SocketClientWithTerminator):
    pass


class BlockingTerminatorHandler(EchoRequestMixin,
                                BaseRequestHandlerWithTerminator):
    pass


class BlockingTerminatorTestMixin(object):
    
    client_class = BlockingTerminatorClient
    handler_class = BlockingTerminatorHandler
    server_class = BlockingServer


class BlockingReadWriteClient(IOClientMixin,
                              SocketClientWithReadWrite):
    pass


class BlockingReadWriteHandler(EchoRequestMixin,
                               BaseRequestHandlerWithReadWrite):
    pass


class BlockingReadWriteTestMixin(object):
    
    client_class = BlockingReadWriteClient
    handler_class = BlockingReadWriteHandler
    server_class = BlockingServer
