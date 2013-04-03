# -*- Mode: Python; coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

import weakref

from kiwi.log import Logger
from kiwi.python import ClassInittableObject

log = Logger(__name__)
# Returned when object is dead
_dead = object()


class _CallbacksList(list):
    """List implementation for working with :class:`_WeakRef` objs"""

    def __contains__(self, item):
        for real_item in iter(self):
            if item == real_item:
                return True

        return False

    def remove(self, item):
        for real_item in iter(self):
            if item == real_item:
                return list.remove(self, real_item)

        # list raises this if could not remove
        raise ValueError


class _WeakRef(object):
    """WeakRef for functions and bound methods

    Slightly based on: http://code.activestate.com/recipes/81253-weakmethod/
    """

    def __init__(self, func):
        try:
            # bound method
            self.obj = weakref.ref(func.im_self)
            self.meth = weakref.ref(func.im_func)
            self.id = id(func.im_func)
        except AttributeError:
            # normal callable
            self.obj = None
            self.meth = weakref.ref(func)
            self.id = id(func)

    def __eq__(self, other):
        if self.id != other.id:
            return False

        # Both are normal callables. Since they have same id, they are equal
        if self.obj is None and other.obj is None:
            return True

        # Both are bound methods, compare their objects to
        # support n objects connecting n events.
        return self.obj() is other.obj()

    def __call__(self, *args, **kwargs):
        func = self.meth()
        if func is None:
            return _dead

        # normal callable
        if self.obj is None:
            return func(*args, **kwargs)

        obj = self.obj()
        if obj is None:
            return _dead

        # bound method
        return func(obj, *args, **kwargs)


class Event(ClassInittableObject):
    """Base class for events"""

    returnclass = None

    @classmethod
    def __class_init__(cls, namespace):
        # We need to set this here because, if the class doesn't define
        # a cls._callbacks_list, Event's one will be used.
        # Also, using a list instead of a set to keep the order
        cls._callbacks_list = _CallbacksList()

    #
    #  Public API
    #

    @classmethod
    def emit(cls, *args, **kwargs):
        log.info('emitting event %s %r %r' % (cls.__name__,
                                              args, kwargs))
        rv_list = []
        for callback in cls._callbacks_list:
            rv = callback(*args, **kwargs)
            if rv is _dead:
                continue
            # Insert in the beggining to pick the last
            # return value which is not None
            rv_list.insert(0, rv)

        # FIXME: Returning just one retval can lead to unpredictable of errors.
        #        We should return al of them and let the one who is
        #        emitting to decide what to do.
        for retval in rv_list:
            if retval is not None:
                if (cls.returnclass and type(retval) != cls.returnclass
                    and not isinstance(retval, cls.returnclass)):
                    raise TypeError('Expected return value to be %s, got %s'
                                    % (cls.returnclass, type(retval)))
                return retval

    @classmethod
    def connect(cls, callback):
        assert callable(callback)
        weak_callback = _WeakRef(callback)
        assert weak_callback not in cls._callbacks_list
        cls._callbacks_list.append(weak_callback)

    @classmethod
    def disconnect(cls, callback):
        cls._callbacks_list.remove(_WeakRef(callback))
