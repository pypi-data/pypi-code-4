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
    name='yo_payments',
    version='0.1.2',
    description='Python Api Wrapper for the Yo Payments service',
    long_description=readme + '\n\n' + history,
    author='James Muranga',
    author_email='jmured@gmail.com',
    url='https://github.com/jamesmura/yo_payments',
    packages=[
	'yo_payments',
    ],
    package_dir={'yo_payments': 'yo_payments'},
    include_package_data=True,
    install_requires=[
        "requests","xmltodict"
    ],
    license="BSD",
    zip_safe=False,
    keywords='yo_payments',
    classifiers=[
	'Development Status :: 2 - Pre-Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: BSD License',
	'Natural Language :: English',
	"Programming Language :: Python :: 2",
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)