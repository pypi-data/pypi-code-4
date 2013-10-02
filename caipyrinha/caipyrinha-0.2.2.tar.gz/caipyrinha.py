#!/usr/bin/env python
# -*- coding: utf-8 -*-

# "THE WISKEY-WARE LICENSE":
# <utn_kdd@googlegroups.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a WISKEY us return.


#===============================================================================
# DOCS
#===============================================================================

"""Abstraction layer over argparse.

Caipyrinha added 2 methods to argparse.ArgumentParser, ``callback`` and
``parse_wc``. Also a Caipyrinha instance is callable and is  equal to use
``parse_wc`` method.


Example of use:

.. code-block:: python

    # ex.py

    import caipyrinha

    parser = caipyrinha.Caipyrinha(prog="Your Program")
    parser.add_argument("--version", action='version', version="%(prog)s 0.1")

    @parser.callback(exit=0, exclusive="group1")
    def first(flags, returns):
        '''Execute this option and exit'''
        print "bye bye"

    @parser.callback(action="store")
    def second(flags, returns):
        '''set his own return value with his parameter'''
        return flags.second

    @parser.callback("--third", exclusive="group1")
    def no_used_name(flags, returns):
        '''you cant use this argument with first'''
        print returns.second

    import sys
    parser(sys.argv[1:])


**Usage**

::

    $ python ex.py --help
    usage: Your Program [-h] [--version] [--first] [--second SECOND] [--third]

    optional arguments:
      -h, --help       show this help message and exit
      --version        show program's version number and exit
      --first          Execute this option and exit
      --second SECOND  set his own return value with his parameter
      --third          you cant use this argument with first
    $ python ex.py --first
    bye bye
    $ python ex.py --first --second "hello from second"
    bye bye
    $ python ex.py --first --second "hello from second" --third
    usage: Your Program [-h] [--version] [--first] [--second SECOND] [--third]
    Your Program: error: argument --third: not allowed with argument --first
    $ python ex.py --second "hello from second" --third
    hello from second


"""

#===============================================================================
# META
#===============================================================================

__version__ = ("0", "2", "2")
__license__ = "WISKEY License"
__author__ = "JBC"
__email__ = "jbc dot develop at gmail dot com"
__url__ = "https://bitbucket.org/leliel12/caipyrinha"

VERSION = ".".join(__version__)


#===============================================================================
# IMPORTS
#===============================================================================

import sys
import argparse
import collections


#===============================================================================
# CLASS
#===============================================================================

class Caipyrinha(argparse.ArgumentParser):
    """Easy argument parser in the top of argparse

    """

    def __init__(self, *args, **kwargs):
        """Creates a new instance of Caipyrinha. Support the same arguments as
        ``argparse.ArgumentParser``

        """
        super(Caipyrinha, self).__init__(*args, **kwargs)
        self._callbacks = collections.OrderedDict()
        self._exgroups = {}

    def __call__(self, args):
        """self.__call__(args) <=> self(args) <=> self.parse_wc(args)"""
        return self.parse_wc(args)

    def callback(self, *args, **kwargs):
        """Decorator for create a new argument and add the function decorated
        ass a callback if the command line argument exists.

        **IMPORTANT:** The callbacks are called in the same order as you
        declared it.

        Support the same ``*args`` and ``**kwargs`` of ``add_argument`` method.
        Also support the ``exclude`` parameter if you want to set the callback
        in a mutually exclusive group, and ``exit`` (must be an int and the
        default is ``None``) if you want to exit after execute this callback
        using this value as exit code.

        The function to be decorated must accept 2 arguments ``flags`` (the
        flag status of the parser) and ``returns`` (the return values of the
        previous callbacks)

        If you dont set the long (``--name``) or short (``-n``) option, the
        name of the function is used as long option. The action by default
        is ``store`` if *nargs* params is setted otherwise ``store_true``.

        for more information please see the
        `argparse <http://docs.python.org/dev/library/argparse.html>`_
        documentation

        """
        args = list(args)
        default_action = "store" if "nargs" in kwargs else "store_true"

        def add_argument(func):
            kwargs["help"] = kwargs.get("help",  (func.__doc__ or "").strip())
            kwargs["action"] = kwargs.get("action", default_action)
            if not len(args):
                args.append("--{}".format(func.__name__))
            exgroup = kwargs.pop("exclusive", None)
            exit = kwargs.pop("exit", None)
            if exgroup and exgroup not in self._exgroups:
                self.add_mutually_exclusive_group(exgroup)
            to_add = self._exgroups[exgroup] if exgroup else self
            added = to_add.add_argument(*args, **kwargs)
            self._callbacks[added.dest] = (func, exit)
            return func

        return add_argument

    def add_mutually_exclusive_group(self, name, required=False):
        """Add a muttually exclusive group as ``argparse.Argparse`` but
        identified by a ``name``. If the ``name`` already exists the same
        group is returned. If ``name`` exists and ``required`` is diferent
        this method change the *required* value.

        """
        if name not in self._exgroups:
            exgroup = super(Caipyrinha, self).add_mutually_exclusive_group()
            self._exgroups[name] = exgroup
        group = self._exgroups[name]
        group.required = required
        return group

    def parse_wc(self, args):
        """Parse the arguments and execute the callbacks.

        :return: The flags and the returns of all the callbacks.

        """

        def dict2namedtuple(name, d):
            args = " ".join(d.keys())
            nt = collections.namedtuple(name, args)
            return nt(**d)

        flags = self.parse_args(args)
        flags_dict = vars(flags)
        returns = dict((k, None) for k in flags_dict.keys())
        for k, v in self._callbacks.items():
            if k in flags_dict and flags_dict[k]:
                callback, exit = self._callbacks[k]
                returns[k] = callback(flags,
                                      dict2namedtuple("Returns", returns))
                if exit is not None:
                    sys.exit(exit)
        return flags, dict2namedtuple("Returns", returns)


#===============================================================================
# MAIN
#===============================================================================

if __name__ == "__main__":
    print(__doc__)
