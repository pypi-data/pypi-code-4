#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A plugin module

Ploit use a plugin system to extend the commands or loaders.
These plugins are registered in Registry class instance.

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'


class CycleIterator(object):
    """
    A base iterator class for infinity cycle
    """
    def __init__(self):
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        """
        Return the current value and increase the index
        """
        current = self.current()
        self.index += 1
        return current

    def current(self):
        """
        Return the current value without increaseing the index
        """
        if self.index >= len(self.iterable):
            self.index = 0
        return self.iterable[self.index]

    def reset(self):
        """
        Reset the index
        """
        self.index = 0
