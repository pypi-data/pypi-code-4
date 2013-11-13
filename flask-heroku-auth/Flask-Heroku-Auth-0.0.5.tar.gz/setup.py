#!/usr/bin/env python

"""
Flask-Heroku-Auth
------------

Simple Decorators for Session Based Oauth, as well as Stateless Basic Auth.
"""

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


setup(
    name='Flask-Heroku-Auth',
    version='0.0.5',
    url='http://github.com/rhyselsmore/flask-heroku-auth',
    author='Rhys Elsmore',
    author_email='me@rhys.io',
    description='Flask Based Heroku Authentication.',
    long_description=open('README.rst').read() + '\n\n' +
        open('HISTORY.rst').read(),
    py_modules=[
        'flask_heroku_auth',
        'flask_heroku_auth.api',
        'flask_heroku_auth.core',
        'flask_heroku_auth.oauth',
        'flask_heroku_auth.utils',
    ],
    license=open('LICENSE').read(),
    package_data={'': ['LICENSE']},
    zip_safe=False,
    platforms='any',
    install_requires=[
        'setuptools',
        'Flask',
        'requests',
        'Flask-OAuth'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
