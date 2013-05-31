##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for z3c.zrtresource package"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='z3c.zrtresource',
      version='1.4.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Resource Templates',
      long_description=(
          read('README.txt')
          + '\n\n.. contents::\n\n' +
          read('src', 'z3c', 'zrtresource', 'README.txt')
          + '\n\n' +
          read('src', 'z3c', 'zrtresource', 'zcml.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 css javascript resource zope",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/z3c.zrtresource',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require = dict(test=['zope.testing',
                                  'zope.traversing',
                                  ]),
      install_requires = ['setuptools',
                          'zope.site',
                          'zope.pagetemplate >= 3.5',
                          'zope.browserresource >= 3.11',
                          'zope.component',
                          'zope.configuration',
                          'zope.interface',
                          'zope.publisher',
                          'zope.schema',
                          'zope.security [untrustedpython]',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
