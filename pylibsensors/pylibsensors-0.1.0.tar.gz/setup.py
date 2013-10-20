#!/usr/bin/env python

# Author: Forest Bond <forest.bond@rapidrollout.com>
# This file is in the public domain.

import os, sys, commands
from distutils.core import Extension


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


from setuplib import setup


def get_version(release_file):
    try:
        f = open(release_file, 'r')
        try:
            return f.read().strip()
        finally:
            f.close()
    except (IOError, OSError):
        status, output = commands.getstatusoutput('bzr revno')
        if status == 0:
            return 'bzr%s' % output.strip()
    return 'unknown'


version = get_version('release')


setup(
  name = 'pylibsensors',
  version = version,
  description = 'libsensors bindings',
  author = 'Forest Bond',
  author_email = 'forest.bond@rapidrollout.com',
  ext_modules = [
    Extension(
      'libsensors',
      sources = ['libsensors.c'],
      libraries = ['sensors'],
      define_macros = [('PYLIBSENSORS_VERSION', '"%s"' % version)],
    ),
  ],
)
