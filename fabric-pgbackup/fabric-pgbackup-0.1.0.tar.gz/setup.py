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

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='fabric-pgbackup',
    version='0.1.0',
    description='PostgreSQL backup/restore utilities for Fabric',
    long_description=readme + '\n\n' + history,
    author='Jakub Zalewski',
    author_email='zalew7@gmail.com',
    url='https://github.com/zalew/fabric-pgbackup',
    packages=[
        'fabric_pgbackup',
    ],
    include_package_data=True,
    install_requires=[
        'fabric',
        'psycopg2',
    ],
    license="MIT",
    zip_safe=False,
    keywords='fabric-pgbackup',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
