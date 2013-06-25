"""
tmtest!
"""

__version_info__ = (1, 0, 0)
__version__ = "1.0.0"

import os
import sys
try:
    import Crypto
except ImportError:
    sys.stderr.write("**WARNING** Could not import 'Crypto': %s")


def tmtest():
    return "this is tmtest"

