#!python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

#  based off the tap2deb code
#  tap2rpm built by Sean Reifschneider, <jafo@tummy.com>

"""
tap2rpm
"""
import sys

try:
    import _preamble
except ImportError:
    sys.exc_clear()

from twisted.scripts import tap2rpm
tap2rpm.run()
