#!/usr/bin/env python
# Copyright (c) 2012 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
import re
from setuptools import setup

VERSIONFILE = "toffee.py"


def get_version():
    return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                     read(VERSIONFILE), re.M).group(1)


def read(*path):
    """\
    Read and return contents of ``path``
    """
    with open(os.path.join(os.path.dirname(__file__), *path),
              'rb') as f:
        return f.read().decode('UTF-8')

setup(
    name='toffee',
    version=get_version(),
    url='https://bitbucket.org/ollyc/toffee',

    license='BSD',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',

    description='',
    long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
    classifiers=['License :: OSI Approved :: BSD License',
                 'Topic :: Software Development :: Testing',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3'],

    py_modules=['toffee'],
    packages=[],

    install_requires=[],
    setup_requires=['nose>=1.0'],
    tests_require=['mock', 'expecter'],
)
