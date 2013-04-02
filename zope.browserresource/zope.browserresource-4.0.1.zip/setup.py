##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""zope.browserresource setup
"""
import os
import sys
from setuptools import setup, find_packages


def test_suite():
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


long_description = (open('README.txt').read() + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.browserresource',
      version='4.0.1',
      url='http://pypi.python.org/pypi/zope.browserresource/',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      classifiers = ['Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.3',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     ],
      description='Browser resources implementation for Zope.',
      long_description=long_description,
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      test_suite='__main__.test_suite',

      namespace_packages=['zope'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zope.component>=3.8.0',
                        'zope.configuration',
                        'zope.contenttype>=4.0.1',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher>=3.8',
                        'zope.schema',
                        'zope.traversing>3.7',
                        ],
      extras_require={
          'test': ['zope.testing'],
          'zcml': ['zope.component[zcml]',
                   'zope.security[zcml]>=3.8'],
          },

      zip_safe = False,
      )
