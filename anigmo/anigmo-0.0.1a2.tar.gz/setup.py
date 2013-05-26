#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import sys

import anigmo
from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
except ImportError:
    print("Could not import Cython.Distutils. Install `cython` and rerun.")
    sys.exit(1)

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

cmdclass = {'build_ext': build_ext}
ext_modules = [
    Extension("anigmo.transpo", ["anigmo/transpo.pyx"]),
    Extension("anigmo.algo", ["anigmo/algo.pyx"]),
    Extension("anigmo.games.connect4", ["anigmo/games/connect4.pyx"]),
    Extension("anigmo.games.tic", ["anigmo/games/tic.pyx"]),
]

# Grab requirments.
with open('reqs.txt') as f:
    required = f.readlines()

tests_require = ['nose']

settings = dict()

settings.update(
    name='anigmo',
    version=anigmo.__version__,
    description='anigmo: artificial intelligence for abstract logic games',
    long_description=open('README.md').read(),
    author=anigmo.__author__,
    author_email='me@cwoebker.com',
    url='anigmo.cwoebker.com',
    download_url='http://github.com/cwoebker/anigmo',
    license=anigmo.__licence__,
    packages=['anigmo', 'anigmo.games'],
    install_requires=required,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ),
)

setup(**settings)
