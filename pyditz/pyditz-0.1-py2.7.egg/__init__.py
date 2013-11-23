"""
Python interface to Ditz (http://ditz.rubyforge.org).
"""

__title__   = "pyditz"
__author__  = 'Glenn Hutchings'
__email__   = 'zondo42@gmail.com'
__version__ = '0.1'
__license__ = 'GPL v2 or later'
__url__     = "https://bitbucket.org/zondo/pyditz"

__classifiers__ = """
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Natural Language :: English
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Operating System :: Unix
Programming Language :: Python :: 2.7
Topic :: Software Development :: Bug Tracking
"""

from database import DitzDB
from commands import DitzCmd
from flags import *
