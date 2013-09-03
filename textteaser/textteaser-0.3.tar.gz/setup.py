#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Jeffrey Goettsch and other contributors.
#
# This file is part of py-textteaser.
#
# py-textteaser is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# py-textteaser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with py-textteaser.  If not, see
# <http://www.gnu.org/licenses/>.


import os
import re
from setuptools import setup


versionfile = os.path.join('textteaser', '_version.py')
versionline = open(versionfile, 'r').read()
versionline_re = r'^__version__ = [\'"]([^\'"]*)[\'"]'
match = re.search(versionline_re, versionline, re.M)
if match:
    __version__ = match.group(1)
else:
    raise RuntimeError('Version string not found in textteaser.')

with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name='textteaser',
    packages=['textteaser', 'textteaser.tests'],
    version=__version__,
    install_requires=['requests==1.2.3'],
    test_suite='nose.collector',
    tests_require=[
        'coverage',
        'nose'],

    # PyPI metadata

    author='Jeffrey Goettsch',
    author_email='jgoettsch+pytextteaser@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: GNU Affero General Public License '
         'v3 or later (AGPLv3+)'),
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: General'],
    description=('A package for summarizing text using the TextTeaser API'),
    download_url=('https://bitbucket.org/jgoettsch/py-textteaser/get/'
                  '{0}.tar.gz').format(__version__),
    long_description=long_description,
    url='https://bitbucket.org/jgoettsch/py-textteaser/',)
