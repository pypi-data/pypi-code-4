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
    name='pyover',
    version='0.1.0',
    description='Python module to interface with pushover.',
    long_description=readme + '\n\n' + history,
    author='Daniël Franke',
    author_email='daniel@ams-sec.org',
    url='https://github.com/ainmosni/pyover',
    packages=[
        'pyover',
    ],
    package_dir={'pyover': 'pyover'},
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    license="BSD",
    zip_safe=False,
    keywords='pyover',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
