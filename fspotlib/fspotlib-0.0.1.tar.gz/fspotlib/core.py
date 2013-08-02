#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Real code of the module.
    This file does not have to be named "core.py".
"""

import json

__all__ = ['say_hello']

def say_hello(to="world"):
    """ this function say hello (printing json on stdout) """
    print json.dumps({"message": "Hello {0}".format(to)}, indent=2)

if __name__ == "__main__":
    say_hello()

