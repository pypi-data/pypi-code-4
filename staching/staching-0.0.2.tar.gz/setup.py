""" setup.py

    Basic setup file to enable pip install

    python setup.py register  sdist upload 

    
"""

import sys
import os
from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 to use stace.")

import staching

setup(name='staching',
      version=staching.__version__,
      description='Compact implementation of Mustache logic-less templating. Fork of Stache.',
      long_description=staching.__doc__,
      author=staching.__author__,
      author_email='smith.samuel.m@gmail.com',
      url='https://github.com/SmithSamuelM/staching',
      py_modules=['staching'],
      scripts=['staching.py'],
      license=staching.__license__,
      platforms = 'any',
     )
