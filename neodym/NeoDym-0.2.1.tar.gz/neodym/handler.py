"""neodym.handler

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
__author__ = "Brian Wiborg <baccenfutter@c-base.org>"
__date__ = "2013/08/31"
__license__ = "GNU/AGPL-3.0"

import logging

from neodym.exceptions import NotYetInitialized, UnregisteredMessage
from neodym.message import Message


class Handler(object):
    """neodym.handler.Handler

    Handlers are helpers for organizing and managing callbacks. This class acts
    as a base-class for all custom handlers you may want to define.

    Handlers have a unique-identifier that must match a unique-identifier of a
    registered message. This identifier indicates what message this handler is
    registered to. Several handlers may be attached to a message, they will be
    called in the order they have been registered when the corresponding
    message arrives.
    """
    __all__ = dict()
    __map__ = dict()

    def __init__(self, unique_identifier):
        """
        :param unique_identifier:   unique-identifier of message this handler
                                    is registered to handle.
        """
        self.unique_identifier = unique_identifier

        self.logger = logging.getLogger('Handler-%s' % id(self))
        self.logger.debug('Initializing: %s' % self)

        if not self.__map__:
            raise NotYetInitialized

        if not self.unique_identifier in self.__map__:
            raise UnregisteredMessage

        if not self.unique_identifier in self.__all__:
            self.__all__[self.unique_identifier] = [self]
        else:
            self.__all__[self.unique_identifier].append(self)

    def __repr__(self):
        """neodym.handler.Handler.__repr__

        Print a nice representation for this handler
        """
        return "<Handler(%s)>" % self.unique_identifier

    def __call__(self, message, connection):
        """neodym.handler.Handler.__call__

        Call this handler.

        :param message:     instance of neodym.message.Message
        :param connection:  instance of neodym.connection.Connection
        """
        self.logger.debug('Received call-back.')
        if not isinstance(message, Message):
            raise TypeError('must be of type neodym.message.Message')

        self.handle(message, connection)
        return self

    def handle(self, message, connection):
        """Overwrite this method in custom handler.
        """
        pass

    def drop(self):
        """neodym.handler.Handler.drop

        Drop this handler so it wont be called on messages any more.
        """
        del self.__all__[self.unique_identifier]

    @classmethod
    def get_handlers(cls, message):
        """neodym.handler.Handler.get_handlers

        Get the list of handlers for a given message.

        :param message:     instance of neodym.message.Message
        """
        if isinstance(message, Message):
            if message.unique_identifier in cls.__map__:
                return cls.__all__[message.unique_identifier]
