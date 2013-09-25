# Copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of python-libmed.
#
# python-libmed is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# python-libmed is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with python-libmed.  If not, see <http://www.gnu.org/licenses/>.

"""
MED: base classes and common functions.
"""
from functools import wraps
from _utils import truncate_name, MEDIOError

class MEDObject(object):
    """ Base class for MED object. """
    def __init__(self, name="", **kwargs):
        super(MEDObject, self).__init__(**kwargs)
        self._name = name

    def _get_name(self):
        return self._name

    name = property(_get_name, None, None, "MED object name.")

    def __repr__(self):
        return '<%s %r at %#x>' % (self.__class__.__name__, self.name,
                                  id(self))

class MEDFileComponents(MEDObject):
    """ Base class for MED file components (mesh, fields, etc.) """
    def __init__(self, name="", **kwargs):
        super(MEDFileComponents, self).__init__(name=truncate_name(name),
                                                **kwargs)

def check_open(func):
    @wraps(func)
    def func_if_open(self, *args, **kwargs):
        if self._closed:
            raise MEDIOError("Closed file, forbidden operation: %s" %
                             func.__name__)
        return func(self, *args, **kwargs)
    return func_if_open

class MEDString(str):
    r"""
    MED string with size fixed by ``size`` and prefilled by \0. ``val``
    defines the leading value.
    When converted to Python string (calling str()), leading and trailing
    spaces and null chars are stripped.

    >>> s = MEDString(4, 'a')
    >>> "%s" % s
    'a'
    >>> "%r" % s
    "'a\\x00\\x00\\x00'"
    >>> s = MEDString(12, 'a   ' * 3)
    >>> str(s[:4])
    'a'
    >>> s =MEDString(3, 'denis')
    >>> s
    'den'
    """
    def __new__(cls, size, val=""):
        return super(MEDString, cls).__new__(cls, val[:size].ljust(size, "\0"))

    def __str__(self):
        return self.strip(" \0")

    def __getitem__(self, key):
        return MEDString(len(self), super(MEDString, self).__getitem__(key))

    def __getslice__(self, start, end):
        return MEDString(len(self),
                         super(MEDString, self).__getslice__(start, end))

    def split_every(self, bs):
        " Split a MEDString every `bs` character "
        return [self[i*bs:(i+1)*bs] for i in range(len(self)/bs)]

