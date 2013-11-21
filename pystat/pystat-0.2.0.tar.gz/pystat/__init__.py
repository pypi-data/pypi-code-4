"""Small library for in-memory aggregation."""

VERSION = (0, 2, 0)

__version__ = '.'.join(map(str, VERSION[0:3]))
__author__ = 'Lipin Dmitriy'
__contact__ = 'blackwithwhite666@gmail.com'
__homepage__ = 'https://github.com/blackwithwhite666/pystat'
__docformat__ = 'restructuredtext'

# -eof meta-

from .counter import Counter
from .timer import Timer
