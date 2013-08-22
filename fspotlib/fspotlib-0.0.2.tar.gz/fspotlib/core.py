#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Real code of the module.
    This file does not have to be named "core.py".
"""

import json
import clize

__all__ = ['say_hi']


def say_hi():
    """ just prints 'Hi'. """
    print "Hi"


@clize.clize
def say_hello(to="world"):
    """ This program says hello (printing json on stdout). """
    print json.dumps({"message": "Hello {0}".format(to)}, indent=2)


def main():
    """ this function is an entry_point for say_hello """
    import sys
    try:
        say_hello(*sys.argv)
    except clize.ArgumentError:
        say_hello(sys.argv[0], '-h')

if __name__ == "__main__":
    main()

