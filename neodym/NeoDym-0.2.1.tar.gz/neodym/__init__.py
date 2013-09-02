"""Neodym

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

import client
import server
import connection
import message
import handler
import exceptions
import logging

# message-mapper for all registered messages
msg_map = message.RegisteredMessageDict(
    handshake=['msg_map_hash']
)

# some shortcuts for our logging wrapper
log_level = logging.INFO
log_format = '%(asctime)16s Neodym %(levelname)10s %(name)32s - %(message)s'


def baseConfig():
    """neodym.baseConfig

    Helper for obtaining a usable logging.baseConfig

    :returns dict:      dictionary with logging configuration
    """
    return {
        'level': log_level,
        'format': log_format,
    }


def init():
    """neodym.init

    Neodym has an initialization and handshaking procedure ensuring both sides
    (e.g. server and all clients) have registered the exactly identical
    message-definitions - see: help(neodym.register) for more information.

    Calling neodym.init() will freeze the registration of new
    message-definitions, generate an md5 hash from neodym.msg_map and pass this hash
    down to all neodym objects.

    Neither client nor server can be initialized before initializing neodym!
    (see: help(neodym.Client) and help(neodym.Server) for more information)
    """
    msg_map_hash = msg_map.hash()
    msg_map.__hash__ = msg_map_hash
    server.Server.__hash__ = msg_map_hash
    client.Client.__hash__ = msg_map_hash
    connection.Connection.__hash__ = msg_map_hash
    message.Message.__map__ = msg_map
    handler.Handler.__map__ = msg_map


def register(unique_identifier, attrs):
    """neodym.register

    Register a new message-definition in the message-mapper. The message-mapper
    is a helper that holds all registered message-definitions.

    A message consists of a unique-identifier and a list of positional
    arguments - see: help(neodym.Message) for more information.

    :param unique_identifier:   unique-identifier of message as string
    :param attrs:               all positional arguments of message as list
    """
    msg_map[unique_identifier] = attrs


# some import shortcuts
from client import Client
from server import Server
from message import Message
from handler import Handler
