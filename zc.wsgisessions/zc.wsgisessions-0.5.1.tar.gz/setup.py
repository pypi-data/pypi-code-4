##############################################################################
#
# Copyright (c) 2011 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""ZC WSGI sessions"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


tests_require = [
    'PasteDeploy',
    'WebTest',
    'ZODB3',
    'bobo',
    'zc.dbconnection',
    'zc.zodbwsgi',
    'zope.testing',
    ]

entry_points = """
[paste.filter_factory]
main = zc.wsgisessions.sessions:BrowserIdFilter
"""


setup(
    name='zc.wsgisessions',
    version='0.5.1',
    author='Zope Corporation',
    author_email='info@zope.com',
    description=__doc__,
    long_description='\n\n'.join([
        read('README.txt'),
        '\n'.join([
            'Detailed Documentation',
            '**********************',
            ]),
        read('src', 'zc', 'wsgisessions', 'sessions.txt'),
        read('CHANGES.txt'),
        ]),
    license='ZPL 2.1',
    keywords=('Zope WSGI session'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'WebOb',
        'setuptools',
        'transaction',
        'zope.component',
        'zope.interface',
        'zope.session',
        ],
    extras_require=dict(
        test=tests_require,
        ),
    tests_require=tests_require,
    test_suite='zc.wsgisessions.tests.test_suite',
    entry_points=entry_points,
    )
