#!/usr/bin/env python
#-*-coding:utf-8-*-

# "THE WISKEY-WARE LICENSE":
# <jbc.develop@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a WISKEY in return Juan BC


#===============================================================================
# DOCS
#===============================================================================

"""Setup for caipyrinha (http://bitbucket.org/leliel12/caipyrinha)"""


#===============================================================================
# IMPORTS
#===============================================================================

import sys


#===============================================================================
# IMPORTS
#===============================================================================

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

import caipyrinha


#===============================================================================
# SETUP
#===============================================================================

DOWNLOAD_URL = "{}/downloads/{}-{}.tar.gz".format(caipyrinha.__url__,
                                                   caipyrinha.VERSION,
                                                   caipyrinha.__name__)

setup(name=caipyrinha.__name__,
      version=caipyrinha.VERSION,
      description=caipyrinha.__doc__.splitlines()[0],
      long_description=caipyrinha.__doc__,
      author=caipyrinha.__author__,
      author_email=caipyrinha.__email__,
      url=caipyrinha.__url__,
      download_url=DOWNLOAD_URL,
      license=caipyrinha.__license__,
      keywords="cli argparse argument parser optparse getopt",
      classifiers=[
                   "Development Status :: 5 - Production/Stable",
                   "Topic :: Utilities",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2",
                   ],
      py_modules = ["caipyrinha", "ez_setup"],
      #test_suite = "test",
)


#===============================================================================
# MAIN
#===============================================================================

if __name__ == '__main__':
    print(__doc__)
