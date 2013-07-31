#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
* Date: 29.07.13
* Time: 0:11
* Original filename: 
"""

from __future__ import print_function, absolute_import
from .parser import Parser
from . import validators

__author__ = 'mosquito'
__all__ = [Parser, validators]
__version__ = "0.4"


__help__ = """
    OptDict
=======

Python module for easy to use command line options. With validation options values and configuration from JSON file.

=== Validations ===

The module provides this validators:
* RequireAll(func1[, func2, ... funcN]) {synonym: Require}
* RequireOnce(func1[, func2, ... funcN])
* ValidAll(name1[, name2 ... nameN]) {synonym: Valid}
* ValidOnce(name1[, name2 ... nameN])
* Conflict(name1[, name2 ... nameN])
* ValidationQueue(Validator0[, Validator1])

"""