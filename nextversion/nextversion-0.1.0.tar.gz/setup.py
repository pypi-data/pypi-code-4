#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import nextversion


setup(
    name          = 'nextversion',
    description   = 'A Python package to generate next version string',
    url           = 'https://github.com/laysakura/nextversion',
    license       = 'LICENSE.txt',
    version       = nextversion.__version__,
    author        = nextversion.__author__,
    author_email  = nextversion.__email__,
    test_suite    = 'nose.collector',
    requires      = [
        'verlib',
    ],
    tests_require = [
        'nose',
        'nose-parameterized',
        'coverage',
    ],
    packages      = [
        'nextversion',
        'nextversion.test'
    ],
    classifiers   = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
