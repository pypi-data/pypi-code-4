##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
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
"""Setup for zopache.pagetemplate package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zopache.pagetemplate',
    version='0.1.0',
    url='http://pypi.python.org/pypi/zopache.pagetemplate',
    author='Christopher Lozinski',
    author_email='lozinski@freerecruiting.com',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    description='ZPT page content component',
    long_description = (
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
        ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zopache'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zope.container',
        'zope.app.publication',
        'zope.formlib',
        'zope.interface',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.size',
        'zope.traversing',
        'ZODB3',
        ],
    extras_require=dict(
        test=[
            'zope.tal >= 3.5.0',
            ]),
    zip_safe=False,
    )
