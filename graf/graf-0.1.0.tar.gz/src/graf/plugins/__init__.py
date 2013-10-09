#!/usr/bin/env python
# coding=utf-8
"""
Plugin module

This module load plugins under this directory recursively.

(C) 2013 hashnote.net, Alisue
"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
__date__    = '2013-10-08'
import pkg_resources
pkg_resources.declare_namespace(__name__)

import os
import sys
from graf.config import settings
from graf.utils.bunch import Bunch


class Registry(object):
    """
    A registry class which store plugin objects
    """

    """entry_point for plugins"""
    ENTRY_POINT = 'graf.plugins'

    def __init__(self):
        self.raw = Bunch()

    def find(self, name, namespace=None):
        """
        Find plugin object

        Args:
            name: a name of the object entry or full namespace
            namespace: a comma separated namespace.

        Usage:
            >>> registry = Registry()
            >>> registry.register('hello', 'goodbye')
            >>> registry.register('foo', 'bar', 'hoge.hoge.hoge')
            >>> registry.register('foobar', 'foobar', 'hoge.hoge')
            >>> registry.find('hello') == 'goodbye'
            True
            >>> registry.find('foo', 'hoge.hoge.hoge') == 'bar'
            True
            >>> registry.find('hoge.hoge.foobar') == 'foobar'
            True

        """
        if "." in name:
            namespace, name = name.rsplit(".", 1)
        caret = self.raw
        if namespace:
            for term in namespace.split('.'):
                if term not in caret:
                    caret[term] = Bunch()
                caret = caret[term]
        return caret[name]

    def register(self, name, obj, namespace=None):
        """
        Register `obj` as `name` in `namespace`

        Args:
            name: a name of the object entry
            obj: a python object which will be registered
            namespace: a comma separated namespace

        Usage:
            >>> registry = Registry()
            >>> registry.register('hello', 'goodbye')
            >>> registry.raw.hello == 'goodbye'
            True
            >>> registry.register('foo', 'bar', 'hoge.hoge.hoge')
            >>> isinstance(registry.raw.hoge, Bunch)
            True
            >>> isinstance(registry.raw.hoge.hoge, Bunch)
            True
            >>> isinstance(registry.raw.hoge.hoge.hoge, Bunch)
            True
            >>> registry.raw.hoge.hoge.hoge.foo == 'bar'
            True
            >>> registry.register('hoge.hoge.foobar', 'foobar')
            >>> registry.raw.hoge.hoge.hoge.foo == 'bar'
            True
            >>> registry.raw.hoge.hoge.foobar == 'foobar'
            True

        """
        if "." in name:
            namespace, name = name.rsplit(".", 1)
        caret = self.raw
        if namespace:
            for term in namespace.split('.'):
                if term not in caret:
                    caret[term] = Bunch()
                caret = caret[term]
        caret[name] = obj

    def load_plugins(self, plugin_dirs=None, quiet=True):
        """
        Load plugins in `sys.path` and `plugin_dirs`

        Args:
            plugin_dirs: a list of plugin directory path
            quiet: if True, print all error message
        """
        from pkg_resources import working_set
        from pkg_resources import iter_entry_points
        from pkg_resources import Environment

        if plugin_dirs is None:
            plugin_dirs = [os.path.dirname(__file__)]
            plugin_dirs += settings['user']['plugin_dirs']

        distributions, errors = working_set.find_plugins(
                Environment(plugin_dirs)
            )
        map(working_set.add, distributions)

        if not quiet:
            # display error info
            for distribution, error in errors:
                print distrubution, error

        for entry_point in iter_entry_points(self.ENTRY_POINT):
            # load entry point
            plugin = entry_point.load()
            # if plugin is callable and `manually` is True, initialize manually
            if callable(plugin) and getattr(plugin, 'manually', False):
                # manually initialize plugin
                plugin(self)
            else:
                # automatically initialize plugin
                self.register(entry_point.name, plugin)

"""A plugin registry"""
registry = Registry()
registry.load_plugins(quiet=False)


def unittest():
    import doctest; doctest.testmod()

if __name__ == '__main__':
    unittest()
