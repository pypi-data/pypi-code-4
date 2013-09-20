#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.md').read().replace('.. :changelog:', '')

setup(
    name='bratabase-social-auth-backend',
    version='0.1.2',
    description='OAuth2 Backend for Bratabase.com to be used with Django-social-auth',
    long_description=readme + '\n\n' + history,
    author='Jj',
    author_email='contact@bratabase.com',
    url='https://github.com/bratabase/bratabase-social-auth-backend',
    packages=[
        'bratabase_social_auth',
        'bratabase_social_auth.backends',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    keywords='bratabase-social-auth-backend',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
