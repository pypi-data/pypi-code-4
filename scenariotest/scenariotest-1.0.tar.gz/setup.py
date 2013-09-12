#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from distutils.core import setup

version = '1.0'
setup(name='scenariotest',
    version=version,
    description=(
        u"Combines a prototypical test case with a list of dictionaries (each "
        u"a dict of keyword arguments) and transforms the two into a series of "
        u"unittest-compatible test cases."),
    author='Jason Webb',
    author_email='bigjasonwebb@gmail.com',
    url='http://github.com/maaku/scenariotest/',
    download_url='http://pypi.python.org/packages/source/s/scenariotest/scenariotest-%s.tar.gz' % version,
    py_modules=['scenariotest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'six>=1.3.0',
    ],
)

#
# End of File
#
