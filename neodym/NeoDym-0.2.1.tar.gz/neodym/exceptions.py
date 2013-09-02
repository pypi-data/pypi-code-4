"""neodym.exception

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

class NeodymException(Exception):
    pass

class NotYetInitialized(NeodymException):
    """Neodym is not yet initialized"""
    def __init__(self):
        NeodymException.__init__(self, self.__doc__)

class AlreadyInitialized(NeodymException):
    """Neodym is already initialized!"""
    def __init__(self):
        NeodymException.__init__(self, self.__doc__)

### Messages ###
class NeodymMessageException(NeodymException):
    pass

class UnregisteredMessage(NeodymMessageException):
    """All transport messages need to be registered before initializing Neodym."""
    def __init__(self):
        NeodymMessageException.__init__(self, self.__doc__)

class MalformedMessage(NeodymMessageException):
    """The message is malformed or invalid"""
    def __init__(self):
        NeodymMessageException.__init__(self, self.__doc__)

class UnknownAttribute(NeodymMessageException):
    """The attribute you are requesting is not an attribute of this message"""
    def __init__(self):
        NeodymMessageException.__init__(self, self.__doc__)
