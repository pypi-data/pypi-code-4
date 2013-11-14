#!/usr/bin/env python

import sys
from setuptools import setup

tests_require = []
if sys.version_info < (2, 7):
    tests_require.append('unittest2')


setup(
    name='werkzeug-encryptedcookie',
    version='1.1',
    url='https://github.com/homm/werkzeug-encryptedcookie',
    author='Alexander Karpinsky',
    author_email='homm86@gmail.com',
    description='Werkzeug encrypted cookie',
    packages=['werkzeug_encryptedcookie'],
    platforms='any',
    install_requires=['PyCrypto>=2.5', 'werkzeug'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=tests_require,
    test_suite='test',
)
