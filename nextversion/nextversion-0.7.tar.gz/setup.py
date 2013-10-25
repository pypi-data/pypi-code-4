#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name             = 'nextversion',
    description      = 'A Python package to generate next version string',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/nextversion',
    license          = 'LICENSE.txt',
    version          = '0.7',
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    install_requires = [
        'verlib',
    ],
    tests_require    = [
        'nose',
        'nose-parameterized',
        'coverage',
    ],
    packages         = [
        'nextversion',
        'nextversion.test'
    ],
    classifiers      = '''
Programming Language :: Python
Development Status :: 5 - Production/Stable
Environment :: Plugins
Intended Audience :: Developers
Topic :: Software Development :: Libraries :: Python Modules
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
License :: OSI Approved :: Apache Software License
'''.strip().splitlines()
)
