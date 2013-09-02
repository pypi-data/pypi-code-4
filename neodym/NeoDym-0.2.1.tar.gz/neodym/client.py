"""neodym.client

Neodym - A thin message-bus wrapper around asyncore.
Copyright (C) 2013  Brian Wiborg <baccenfutter@c-base.org>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__ = "Brian Wiborg <baccenfutter@c-base.org"
__date__ = "2013/08/31"
__license__ = "GNU/AGPL-3.0"

import asyncore
import logging
import socket

from neodym.connection import Connection
from neodym.message import Message


class Client(asyncore.dispatcher):
    """neodym.client.Client

    The client connects to a server and tries to establish a connection by
    performing a handshaking procedure. If the handshake completes
    successfully, the client can send messages to the server.
    """
    __hash__ = ""

    def __init__(self, host, port):
        """
        :param host:    hostname or ip of server as string
        :param port:    TCP port as integer
        """
        self.host = host
        self.port = port
        asyncore.dispatcher.__init__(self)

        self.logger = logging.getLogger('Client-%s' % id(self))
        self.logger.debug('Initializing: %s' % self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__connection = None

    def handle_connect(self):
        """asyncore.handle_connect
        """
        self.logger.info('Connected to server, establishing connection...')
        self.__connection = Connection(self.socket, self)

    def handle_close(self):
        """asyncore.handle_close
        """
        self.logger.info('Closing.')
        Connection.__all__ = set()

    def client_connect(self):
        """neodym.client.Client.client_connect

        Connect to server.
        """
        self.connect((self.host, self.port))
        pass
        self.update()
        pass

    def update(self):
        """neodym.client.Client.update

        Poll asyncore, pass and return.
        """
        asyncore.poll2()
        pass
        return

    def connection(self):
        """neodym.client.Client.connection

        Obtain an established connection from the client by performing the
        handshaking procedure with the server.

        :returns neodym.connection.Connection:  the connection instance
        """
        handshake = Message('handshake', [self.__hash__])
        self.__connection.put(handshake)

        while self.__connection.recv_queue.empty():
            self.update()

        message = self.__connection.recv_queue.get()
        if not message:
            self.logger.info('Timeout reached!')
            self.close()
        elif message.unique_identifier == 'handshake':
            self.logger.info('Connection established.')
            return self.__connection
