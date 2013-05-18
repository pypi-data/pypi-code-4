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
    'iniparse >= 0.4'
]

setup(
    name='templet',
    version='0.0.6',
    description='Simple scaffolding tool',
    long_description=open('README.md').read(),
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
