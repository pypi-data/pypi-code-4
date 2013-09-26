#!/usr/bin/env python

import os
import sys

import txrequests

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'txrequests',
]

requires = [
    'requests>=1.2.0',
    'twisted>=9.0.0'
]

setup(
    name='txrequests',
    version=txrequests.__version__,
    description='Asynchronous Python HTTP for Humans.',
    long_description=open('README.rst').read(),
    author='Pierre Tardy',
    author_email='tardyp@gmail.com',
    packages=packages,
    package_dir={'txrequests': 'txrequests'},
    package_data={'txrequests': ['LICENSE', 'README.rst']},
    include_package_data=True,
    install_requires=requires,
    license='Apache License v2',
    url='https://github.com/tardyp/txrequests',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
