##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.annotation package
"""
import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def alltests():
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    from zope.testrunner.options import get_options
    from zope.testrunner.find import find_suites
    from unittest import TestSuite
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    src = os.path.join(here, 'src')
    defaults = ['--test-path', src]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)

setup(
    name='zope.annotation',
    version='4.2.0',
    url='http://pypi.python.org/pypi/zope.annotation',
    license='ZPL 2.1',
    description='Object annotation mechanism',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        ],
    long_description= \
        read('src', 'zope', 'annotation', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope',],
    install_requires=[
        'BTrees',
        'setuptools',
        'zope.interface',
        'zope.component',
        'zope.location',
        'zope.proxy',
        ],
    extras_require=dict(
        test=[
            'persistent',
            'zope.testing'
            ],
        zcml=[
            'zope.component[zcml]',
            'zope.configuration',
            ],
        ),
    test_suite="__main__.alltests",
    tests_require=[
        'persistent',
        'zope.component[zcml]',
        'zope.configuration',
        'zope.testrunner',
        'zope.testing'],
    include_package_data=True,
    zip_safe=False,
    )
