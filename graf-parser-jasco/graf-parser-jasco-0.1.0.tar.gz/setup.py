#!/usr/bin/env python
# coding=utf-8
"""
graf-parser-jasco

Graf plugin which allow to read JASCO (http://www.jasco.co.jp/) txt file

Usage:
    >>> 

(C) 2013 hashnote.net, Alisue
"""
name = 'graf-parser-jasco'
version = '0.1.0'
author = 'Alisue'
author_email = 'lambdalisue@hashnote.net'

import os
from setuptools import setup, find_packages

setup(
    name=name,
    version=version,
    description = "Graf parser plugin for reading JASCO txt file",
    long_description=__doc__,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords = "graf, JASCO, parser",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_package = [
        'graf',
        'graf.builtins',
        'graf.plugins',
        'graf.plugins.filters',
        'graf.plugins.parsers',
        'graf.plugins.loaders',
    ],
    include_package_data = True,
    exclude_package_data = {'': ['README.md']},
    zip_safe = True,
    install_requires=[
        'graf',
    ],
    entry_points={
        'graf.plugins': [
            'parsers.JASCOParser = graf.plugins.parsers.jasco:JASCOParser',
        ],
    },
)

