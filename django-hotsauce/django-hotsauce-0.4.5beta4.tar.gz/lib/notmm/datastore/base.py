#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2011 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
#
# This file is part of the notmm distribution.
# Please review the LICENSE file for details.

"""DataStore API

The DataStore API provides a simplified environment for storing
user/system data. It should be noted that the current state of 
the API is still in an early alpha stage and is subject to change.
"""

__all__ = ['DataStore']

from notmm.utils.configparse import is_uppercase


class DataStore(object):
    """Base class for storing and loading objects."""

    def __init__(self):
        pass

    def count(self):
        """
        count the number of objects in UPPER_CASE found
        in __dict__ and return that number. Note that
        only UPPER_CASE keys are being counted.
        """
        return len([ key for key in self.__dict__ if is_uppercase(key) ])  

    def clear(self):
        """ remove everything that looks like a setting option """
        for key, val in self.__dict__.items():
            if is_uppercase(key):
                del self.__dict__[key]
        # reset the initialized object..
        #self.initialized = False
        # and always return something..
        return self

