#!python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import os, sys

try:
    import _preamble
except ImportError:
    sys.exc_clear()

# begin chdir armor
sys.path[:] = map(os.path.abspath, sys.path)
# end chdir armor

sys.path.insert(0, os.path.abspath(os.getcwd()))

from twisted.scripts.trial import run
run()
