#
# setup.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See file LICENSE)
#

"""Setup script for the scope library."""

from distutils.core import setup

NAME = 'scope'
VERSION = '0.1.1'
DESCRIPTION = 'Template library for multi-language code generation'
AUTHOR = 'Luis Garcia'
AUTHOR_EMAIL = 'lgarcia@codespot.in'
URL = 'https://github.com/lrgar/scope'
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: C++',
    'Programming Language :: Python',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Libraries'
]
LICENSE = 'MIT'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=['scope', 'scope.lang'],
    license=LICENSE,
    classifiers=CLASSIFIERS
)
