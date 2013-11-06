#!/usr/bin/env python
# Copyright (C) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
# See LICENSE for copyright info.
"""Thread-local Storage API"""

import posixpath

from .base import DataStore

__all__ = ('ThreadLocalStore',)

class ThreadLocalStore(DataStore):
    """Wrapper to store local data in a single thread"""
   
    _initialized = False
    
    def __init__(self, modname=None, autoload=False):
        """Implements the __init__ method for ThreadLocalStore instances.
        
        Automatically load the objects contained in ``modname`` if autoload is True.
        """

        # This init code was borrowed from the 
        # _threading_local module.
        self.modname = modname
        self.initialized = False

        if autoload: 
            self.loads(modname)

    def loads(self, modname=None):
        """ 
        Load objects from `modname` using the `__import__`
        builtin function.
        """
        if not modname:
            modname = self.modname

        head, tail = posixpath.splitext(modname)
        module_name = tail.lstrip('.')
        # this must handle both absolute and relative imports
        m_obj = __import__(modname, {}, {}, fromlist=[module_name])
        # Copy the precious settings into our thread-safe 
        # storing class.
        if m_obj:
            self.__dict__ = m_obj.__dict__.copy()
            self.initialized = True

        return self

    def __iter__(self):
        return iter(self.__dict__)

    def __next__(self):
        for item in self.__dict__.iteritems():
            yield item
    
    def __getitem__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise

    def __setitem__(self, name, value):
        try:
            self.__dict__[name] = value
        except Exception:
            raise

    def __str__(self):
        return "%s" % self.modname

