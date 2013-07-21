#! /usr/bin/env python

import sys
from distutils.core import setup


if 'upload' in sys.argv:
    if '--sign' not in sys.argv and sys.argv[1:] != ['upload', '--help']:
        raise SystemExit('Refusing to upload unsigned packages.')


setup(name = 'concon',
      description = 'CONstrained CONtainers: immutable and append-only container subclasses and utilities.',
      url = 'https://bitbucket.org/nejucomo/concon',
      license = 'MIT (see LICENSE.txt)',
      version = '0.2',
      author = 'Nathan Wilcox',
      author_email = 'nejucomo@gmail.com',
      py_modules = ['concon'],
      )
