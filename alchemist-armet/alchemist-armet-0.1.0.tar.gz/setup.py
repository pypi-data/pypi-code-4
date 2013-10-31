#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from imp import load_source
import sys

test_requirements = []
if sys.version_info[0] < 3:
    test_requirements += ['mock']


setup(
    name='alchemist-armet',
    version=load_source('', 'alchemist_armet/_version.py').__version__,
    description='Tight integration of armet with alchemist.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        # 'Framework :: SQLAlchemy',
        # 'Framework :: Alchemist',
        # 'Framework :: Armet',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/alchemist-armet',
    packages=find_packages('.'),
    install_requires=[
        'alchemist >= 0.3.0',
        'armet >= 0.4.0'
    ],
)
