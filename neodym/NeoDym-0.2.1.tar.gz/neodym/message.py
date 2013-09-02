"""neodym.message.Message

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

import logging
import UserDict
import hashlib
import json

from neodym.exceptions import (AlreadyInitialized, MalformedMessage,
                               UnregisteredMessage, UnknownAttribute)


class RegisteredMessageDict(UserDict.IterableUserDict):
    """neodym.message.RegisteredMessageDict

    This is the message-mapper holding all registered messages of this neodym instance.

    The message-mapper behaves like a regular dictionary, except that it has an extra
    method for generating an md5 hash over all registered messages for the handshaking
    procedure.

    The message-mapper can be initialized in three different ways:

        - msg_map = neodym.message.RegisteredMessageDict()
        - msg_map = neodym.message.RegisteredMessageDict({'foo': 'bar'})
        - msg_map = neodym.message.RegisteredMessageDict(foo=bar)

    There should always exist only one message-mapper!
    """
    # todo: refactor towards singleton
    __hash__ = ""

    def __init__(self, *args, **kwargs):
        self.data = {}

        self.logger = logging.getLogger('RegisteredMessageDict')
        self.logger.info('Initializing: %s' % self)

        UserDict.IterableUserDict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        """neodym.message.RegisteredMessageDict.__setitem__

        Items can only be set while neodym is not yet initialized.

        :raises: AlreadyInitialized:    if neodym is already initialized
        """
        if self.__hash__:
            raise AlreadyInitialized

        if not isinstance(key, str) or not isinstance(value, list):
            raise ValueError('Key must be a string and value must be a list!')
        self.data[key] = value

    def __delitem__(self, key):
        """neodym.message.RegisteredMessageDict.__delitem__

        Items can only be deleted while neodym has not yet been initialized.

        :raises AlreadyInitialized:     if neodym has already been initialized
        """
        if self.__hash__:
            raise AlreadyInitialized

    def hash(self):
        """neodym.message.RegisteredMessageDict.hash

        Return the md5 hash for all currently registered messages.

        :returns str:   md5 hex-digest
        """
        msg_map = [(k, self.data[k]) for k in sorted(self.data)]
        return hashlib.md5(str(msg_map)).hexdigest()


class Message(object):
    """neodym.message.Message

    Messages are the core elements of neodym network communications. They are
    the atom element that is sent over the wire.

    All messages need to be registered before initializing neodym. Only clients
    with matching message-mapper hashes are allowed to connect with the server.
    This measure insures that both parties are able to interpret all possible
    messages equally.

    Only messages that have been registered with neodym will be able to be
    initialized. Initializing a message that hasn't been registered with neodym
    will result in an neodym.exceptions.MalformedMessage.

    A message consists of a unique_identifier and a list of positional
    attributes. The length of the positional attributes must be equal to the
    length of the positional attribute-names in the message-mapper, and
    additionally in the identical order!
    """
    __map__ = dict()    # dictionary of all registered messages

    def __init__(self, unique_identifier, attrs):
        """
        :param unique_identifier:   unique-identifier of message as string
        :param attrs:               list of positional attributes of message
        """
        self.unique_identifier = unique_identifier
        self.attrs = attrs

        self.logger = logging.getLogger('Message-%s' % id(self))
        self.logger.debug('Initializing: %s' % self)

        if not (
            isinstance(self.unique_identifier, str) and
            isinstance(self.attrs, list)
        ):
            raise MalformedMessage

        if not (
            self.unique_identifier in self.__map__ and
            len(self.attrs) == len(self.__map__[self.unique_identifier])
        ):
            raise UnregisteredMessage

        if not self.unique_identifier in self.__map__:
            raise UnregisteredMessage

    def __repr__(self):
        """neodym.message.Message.__repr__

        Print a nice representation of this message.
        """
        return "<Neodym.Message(%s)>" % self.pack()[:-2]

    def get_attr(self, attr):
        """neodym.message.Message.get_attr

        Get a specific message-attribute. Will raise an exception if the
        attribute doesn't exist.

        :returns attr:

        :raises neodym.exceptions.UnknownAttribute:     if attr is unknown
        """
        if not attr in self.__map__[self.unique_identifier]:
            raise UnknownAttribute

        index = self.__map__[self.unique_identifier].index(attr)
        return self.attrs[index]

    def set_attr(self, attr, value):
        """neodym.message.Message.set_attr

        Set a specific message-attribute to a given value. Will raise an
        exception if the attribute doesn't exist.

        :raises neodym.exceptions.UnknownAttribute:     if attr is unknown
        """
        if not attr in self.__map__[self.unique_identifier]:
            raise UnknownAttribute

        index = self.__map__[self.unique_identifier].index(attr)
        self.attrs[index] = value

    def get_attrs(self):
        """neodym.message.Message.get_attrs

        Return a list of tuples of all attribute-names and their values, e.g.
        [('my_attr_name', 'my_attr_value), ... ]

        Hint:   dict(neodym.message.Message.get_attrs) will return a dict of
                all message-attributes mapped to their attribute-names.
        """
        return zip(self.__map__[self.unique_identifier], self.attrs)

    def set_attrs(self, attrs):
        """neodym.message.Message.set_attrs

        Bulk-set many message-attributes to given values. Will raise an
        exception if any of the attribute-names doesn't exist.

        :param attrs:   dictionary containing attribute-names and -values
        """
        if not isinstance(attrs, dict):
            raise TypeError('Attributes must be passed as dictionary!')

        for attr, value in attrs.items():
            self.set_attr(attr, value)

    def pack(self):
        """neodym.message.Message.pack

        Return JSON representation of this message with trailing
        carriage-return and newline.
        """
        return json.dumps({self.unique_identifier: self.attrs}) + '\r\n'

    @classmethod
    def unpack(cls, line):
        """neodym.message.Message.unpack

        Class-method for unpacking a given string into a
        neodym.message.Message. Will return None if the message couldn't be
        unpacked.

        :param line:    arbitrary string

        :returns neodym.message.Message:    if message could be unpacked
        """
        try:
            message = json.loads(line.strip())
            unique_identifier, attrs = message.items()[0]
            return Message(str(unique_identifier), attrs)
        except:
            logging.debug('Error while unpacking line: %s' % line)

