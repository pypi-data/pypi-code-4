#!/usr/bin/env python2

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = [
    'templet'
]


requires = [
    'Jinja2 >= 2.6',
    'clint >= 0.3.1'
]

setup(
    name='templet',
    version='0.1.3',
    description='Simple scaffolding tool',
    long_description=open('README.rst').read(),
    author='Alexandr Skurikhin',
    author_email='a@skurih.in',
    url='git://skurih.in/templet.git',
    scripts=['bin/templet'],
    packages=packages,
    package_data={'': ['LICENSE']},
    install_requires=requires,
    license=open('LICENSE').read(),
)

del os.environ['PYTHONDONTWRITEBYTECODE']
