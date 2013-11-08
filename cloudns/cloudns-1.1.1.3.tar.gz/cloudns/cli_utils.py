#!/usr/bin/env python
# coding=utf-8

"""
utilities for the CLI interface.
"""

import sys


CONSOLE_ENCODING = 'utf-8'
PY3 = sys.version_info[0] == 3


def _encode(fmt, *args):
    s = (fmt % args) if args else fmt
    if PY3:
        return s
    else:
        return s.encode(CONSOLE_ENCODING)


def out(fmt, *args):
    """Prints a unicode message to stdout."""
    sys.stdout.write(_encode(fmt, *args))


def warn(fmt, *args):
    """Prints a unicode message to stderr."""
    sys.stderr.write(_encode(fmt, *args))


def err(fmt, *args):
    """Prints a unicode message to stderr and flush buffer."""
    sys.stderr.write(_encode(fmt, *args))
    sys.stderr.flush()
