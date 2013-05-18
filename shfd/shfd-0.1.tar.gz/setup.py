# -*- coding: utf-8 -*-

import os
import sys
import shfd


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = []


setup(
    name='shfd',
    version=shfd.__version__,
    description='Sh for dummies',
    long_description=open('README.rst').read(),
    author='Morgotth',
    author_email='morgotth0@gmail.com',
    url='https://github.com/morgotth/shfd',
    py_modules=['shfd'],
    install_requires=required,
    license=shfd.__licence__,
    platforms = 'any',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Freeware',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
