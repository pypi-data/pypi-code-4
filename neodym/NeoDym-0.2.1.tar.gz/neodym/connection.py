"""neodym.connection

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
import Queue

from neodym.exceptions import MalformedMessage
from neodym.message import Message


class Connection(asyncore.dispatcher):
    """neodym.connection.Connection

    A connection is an asyncore.dispatcher acting as a communication interface
    between client and server. From client-view, the connection is the
    representation of the server. From server-view, each connection represents
    a connected client.
    """
    __all__ = []
    __hash__ = ""
    __chunk__ = 8192
    __timeout__ = 30

    def __init__(self, sock, parent):
        """
        :param sock:    socket.socket
        :param parent:  instance either of neodym.server.Server or
                        neodym.client.Client
        """
        asyncore.dispatcher.__init__(self, sock=sock)
        self.parent = parent

        self.logger = logging.getLogger('Connection-%s' % id(self))
        self.logger.debug('Initializing: %s' % self)

        self.send_queue = Queue.Queue()
        self.recv_queue = Queue.Queue()

        self.is_connected = False
        Connection.__all__.append(self)

    def __del__(self):
        """neodym.connection.Connection.__del__

        Leave a short note in the server logs about the terminating connection.
        """
        self.logger.info('Terminated.')

    def writable(self):
        """asyncore.dispatcher.writable
        """
        return not self.send_queue.empty()

    def handle_read(self):
        """asyncore.dispatcher.handle_read
        """
        self.logger.debug('Data incoming...')
        chunk = self.recv(self.__chunk__)
        if not chunk:
            self.close()

        lines = chunk.replace('\r\n', '\n').split('\n')
        self.logger.debug('Received data: %s' % str(lines))

        for line in lines:
            if line:
                message = Message.unpack(line)
                if message:
                    self.recv_queue.put(message)
                else:
                    self.logger.debug('Can not unpack message: %s' % str(message))

    def handle_write(self):
        """asyncore.dispatcher.handle_write
        """
        message = self.send_queue.get()
        self.logger.debug('Handling write: %s' % message)
        if isinstance(message, Message):
            self.send(message.pack())
        else:
            self.send(str(message) + '\r\n')

    def handle_close(self):
        """asyncore.dispatcher.handle_close
        """
        self.logger.debug('Closing!')
        self.drop()

    def put(self, message):
        """neodym.connection.Connection.put

        Put a message into the send-queue.

        :param message:     instance of neodym.message.Message
        """
        self.logger.debug('Throwing message into send queue: %s' % message)
        if not isinstance(message, Message):
            raise MalformedMessage

        self.send_queue.put(message)

    def get(self):
        """neodym.connection.Connection.get

        Poll the receive-queue for any new messages that may have arrived.

        :returns neodym.message.Message:    if a message is in the queue
        :returns None                       if queue is empty
        """
        self.logger.debug('Polling receive queue for messages')
        if not self.recv_queue.empty():
            return self.recv_queue.get()

    def drop(self):
        """neodym.connection.Connection.drop

        Drop this connection from the list of all connections, e.g. as a
        preparation for closing the connection.
        """
        if self in self.__all__:
            self.__all__.remove(self)
