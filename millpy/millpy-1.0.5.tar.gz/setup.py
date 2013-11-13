#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'millpy',
]

requires = [
    'requests>=1.0.0,<1.1.0',
]

tests_require = [
    'nose',
    'rednose',
    'pep8',
    'pyflakes',
]

setup(
    name='millpy',
    version='1.0.5',
    description='Paymill for Python.',
    author='Nick Bruun',
    author_email='nick@bruun.co',
    url='http://bruun.co/',
    packages=packages,
    package_dir={'millpy': 'millpy'},
    include_package_data=True,
    install_requires=requires,
    tests_require=tests_require,
    #license=open('LICENSE').read(),
    zip_safe=True,
)
