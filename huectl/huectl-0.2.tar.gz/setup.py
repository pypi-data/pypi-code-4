#!/usr/bin/env python

from setuptools import setup
from huecontroller import __version__
import huecontroller as hctl

setup(name='huectl',
      version          = __version__,
      author           = 'Christian Kellner',
      author_email     = 'christian@kellner.me',
      url              = 'https://github.com/gicmo/huectl',
      license          = 'WTFPL',
      description      = hctl.__doc__.split("\n")[1],
      long_description = hctl.__doc__,
      py_modules       = ['huecontroller'],
      scripts          = ['huectl'],
      install_requires = ['phue'],
      platforms        = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      )
