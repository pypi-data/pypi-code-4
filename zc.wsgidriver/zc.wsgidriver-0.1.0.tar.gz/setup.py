##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
name, version = 'zc.wsgidriver', '0.1.0'

install_requires = ['setuptools', 'manuel', 'zope.testing',
                    'selenium', 'zc.customdoctests']
extras_require = dict(test=['bobo', 'zope.testing'])

entry_points = """
"""

from setuptools import setup

long_description = open('README.rst').read()

setup(
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',

    name = name, version = version,
    long_description=long_description,
    description = long_description.strip().split('\n')[0],
    packages = ['zc', name],
    namespace_packages = [name.split('.')[0]],
    package_dir = {'': 'src'},
    install_requires = install_requires,
    zip_safe = False,
    entry_points=entry_points,
    extras_require = extras_require,
    package_data = {name: ['*.rst', '*.txt', '*.test', '*.html']},
    )
