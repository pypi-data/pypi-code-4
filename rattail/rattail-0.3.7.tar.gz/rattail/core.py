#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Core Stuff
"""

from uuid import uuid1


__all__ = ['Object', 'get_uuid']


class Object(object):
    """
    Generic base class.

    This is used mostly for convenience.
    """

    def __init__(self, **kwargs):
        """
        Constructor which assigns keyword arguments as attributes.
        """

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __getitem__(self, key):
        """
        Allows dict-like access to the object's attributes.
        """

        if hasattr(self, key):
            return getattr(self, key)

    def __str__(self):
        """
        Magic string method.

        This leverages :meth:`__unicode__()` if it exists; otherwise falls back
        to ``repr(self)``.
        """

        if hasattr(self, '__unicode__'):
            return str(unicode(self))
        return repr(self)


def get_uuid():
    """
    Generate a universally-unique identifier.

    :returns: A 32-character hex string.
    """

    return uuid1().hex
