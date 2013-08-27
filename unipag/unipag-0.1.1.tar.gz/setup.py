#!/usr/bin/env python

import os
import unipag

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = ['unipag']
requires = ['requests>=0.9']

setup(
    name='unipag',
    version=unipag.__version__,
    description='Unipag Client for Python',
    long_description=open('README.rst').read(),
    author='Denis Stebunov',
    author_email='support@unipag.com',
    url='https://github.com/unipag/unipag-python',
    packages=packages,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)

del os.environ['PYTHONDONTWRITEBYTECODE']