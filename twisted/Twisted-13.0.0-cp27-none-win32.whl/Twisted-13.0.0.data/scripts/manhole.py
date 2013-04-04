#!python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This script runs GtkManhole, a client for Twisted.Manhole
"""
import sys

try:
    import _preamble
except ImportError:
    sys.exc_clear()

from twisted.scripts import manhole
manhole.run()
