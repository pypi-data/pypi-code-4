#!/usr/bin/env python
#
# Copyright 2011 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A non-blocking, single-threaded TCP server."""
from __future__ import absolute_import, division, print_function, with_statement

import errno
import os
import socket
import ssl

from tornado.log import app_log
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream, SSLIOStream
from tornado.netutil import bind_sockets, add_accept_handler, ssl_wrap_socket
from tornado import process


class TCPServer(object):
    r"""A non-blocking, single-threaded TCP server.

    To use `TCPServer`, define a subclass which overrides the `handle_stream`
    method.

    To make this server serve SSL traffic, send the ssl_options dictionary
    argument with the arguments required for the `ssl.wrap_socket` method,
    including "certfile" and "keyfile"::

       TCPServer(ssl_options={
           "certfile": os.path.join(data_dir, "mydomain.crt"),
           "keyfile": os.path.join(data_dir, "mydomain.key"),
       })

    `TCPServer` initialization follows one of three patterns:

    1. `listen`: simple single-process::

            server = TCPServer()
            server.listen(8888)
            IOLoop.instance().start()

    2. `bind`/`start`: simple multi-process::

            server = TCPServer()
            server.bind(8888)
            server.start(0)  # Forks multiple sub-processes
            IOLoop.instance().start()

       When using this interface, an `.IOLoop` must *not* be passed
       to the `TCPServer` constructor.  `start` will always start
       the server on the default singleton `.IOLoop`.

    3. `add_sockets`: advanced multi-process::

            sockets = bind_sockets(8888)
            tornado.process.fork_processes(0)
            server = TCPServer()
            server.add_sockets(sockets)
            IOLoop.instance().start()

       The `add_sockets` interface is more complicated, but it can be
       used with `tornado.process.fork_processes` to give you more
       flexibility in when the fork happens.  `add_sockets` can
       also be used in single-process servers if you want to create
       your listening sockets in some way other than
       `~tornado.netutil.bind_sockets`.
    """
    def __init__(self, io_loop=None, ssl_options=None):
        self.io_loop = io_loop
        self.ssl_options = ssl_options
        self._sockets = {}  # fd -> socket object
        self._pending_sockets = []
        self._started = False

        # Verify the SSL options. Otherwise we don't get errors until clients
        # connect. This doesn't verify that the keys are legitimate, but
        # the SSL module doesn't do that until there is a connected socket
        # which seems like too much work
        if self.ssl_options is not None and isinstance(self.ssl_options, dict):
            # Only certfile is required: it can contain both keys
            if 'certfile' not in self.ssl_options:
                raise KeyError('missing key "certfile" in ssl_options')

            if not os.path.exists(self.ssl_options['certfile']):
                raise ValueError('certfile "%s" does not exist' %
                                 self.ssl_options['certfile'])
            if ('keyfile' in self.ssl_options and
                    not os.path.exists(self.ssl_options['keyfile'])):
                raise ValueError('keyfile "%s" does not exist' %
                                 self.ssl_options['keyfile'])

    def listen(self, port, address=""):
        """Starts accepting connections on the given port.

        This method may be called more than once to listen on multiple ports.
        `listen` takes effect immediately; it is not necessary to call
        `TCPServer.start` afterwards.  It is, however, necessary to start
        the `.IOLoop`.
        """
        sockets = bind_sockets(port, address=address)
        self.add_sockets(sockets)

    def add_sockets(self, sockets):
        """Makes this server start accepting connections on the given sockets.

        The ``sockets`` parameter is a list of socket objects such as
        those returned by `~tornado.netutil.bind_sockets`.
        `add_sockets` is typically used in combination with that
        method and `tornado.process.fork_processes` to provide greater
        control over the initialization of a multi-process server.
        """
        if self.io_loop is None:
            self.io_loop = IOLoop.current()

        for sock in sockets:
            self._sockets[sock.fileno()] = sock
            add_accept_handler(sock, self._handle_connection,
                               io_loop=self.io_loop)

    def add_socket(self, socket):
        """Singular version of `add_sockets`.  Takes a single socket object."""
        self.add_sockets([socket])

    def bind(self, port, address=None, family=socket.AF_UNSPEC, backlog=128):
        """Binds this server to the given port on the given address.

        To start the server, call `start`. If you want to run this server
        in a single process, you can call `listen` as a shortcut to the
        sequence of `bind` and `start` calls.

        Address may be either an IP address or hostname.  If it's a hostname,
        the server will listen on all IP addresses associated with the
        name.  Address may be an empty string or None to listen on all
        available interfaces.  Family may be set to either `socket.AF_INET`
        or `socket.AF_INET6` to restrict to IPv4 or IPv6 addresses, otherwise
        both will be used if available.

        The ``backlog`` argument has the same meaning as for
        `socket.listen <socket.socket.listen>`.

        This method may be called multiple times prior to `start` to listen
        on multiple ports or interfaces.
        """
        sockets = bind_sockets(port, address=address, family=family,
                               backlog=backlog)
        if self._started:
            self.add_sockets(sockets)
        else:
            self._pending_sockets.extend(sockets)

    def start(self, num_processes=1):
        """Starts this server in the `.IOLoop`.

        By default, we run the server in this process and do not fork any
        additional child process.

        If num_processes is ``None`` or <= 0, we detect the number of cores
        available on this machine and fork that number of child
        processes. If num_processes is given and > 1, we fork that
        specific number of sub-processes.

        Since we use processes and not threads, there is no shared memory
        between any server code.

        Note that multiple processes are not compatible with the autoreload
        module (or the ``debug=True`` option to `tornado.web.Application`).
        When using multiple processes, no IOLoops can be created or
        referenced until after the call to ``TCPServer.start(n)``.
        """
        assert not self._started
        self._started = True
        if num_processes != 1:
            process.fork_processes(num_processes)
        sockets = self._pending_sockets
        self._pending_sockets = []
        self.add_sockets(sockets)

    def stop(self):
        """Stops listening for new connections.

        Requests currently in progress may still continue after the
        server is stopped.
        """
        for fd, sock in self._sockets.items():
            self.io_loop.remove_handler(fd)
            sock.close()

    def handle_stream(self, stream, address):
        """Override to handle a new `.IOStream` from an incoming connection."""
        raise NotImplementedError()

    def _handle_connection(self, connection, address):
        if self.ssl_options is not None:
            assert ssl, "Python 2.6+ and OpenSSL required for SSL"
            try:
                connection = ssl_wrap_socket(connection,
                                             self.ssl_options,
                                             server_side=True,
                                             do_handshake_on_connect=False)
            except ssl.SSLError as err:
                if err.args[0] == ssl.SSL_ERROR_EOF:
                    return connection.close()
                else:
                    raise
            except socket.error as err:
                if err.args[0] == errno.ECONNABORTED:
                    return connection.close()
                else:
                    raise
        try:
            if self.ssl_options is not None:
                stream = SSLIOStream(connection, io_loop=self.io_loop)
            else:
                stream = IOStream(connection, io_loop=self.io_loop)
            self.handle_stream(stream, address)
        except Exception:
            app_log.error("Error in connection callback", exc_info=True)
