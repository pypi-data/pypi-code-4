#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from distutils.core import setup
from lookahead import get_version

version = get_version().replace(' ', '-')
setup(name='lookahead',
    version=version,
    description=(
        u"Provides a utility for constructing generators out of an iterable "
        u"that yield look-ahead (and/or “look-behind”) tuples."),
    author='Mark Friedenbach',
    author_email='mark@friedenbach.org',
    url='http://github.com/maaku/lookahead/',
    download_url='http://pypi.python.org/packages/source/l/lookahead/lookahead-%s.tar.gz' % version,
    py_modules=('lookahead',),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
