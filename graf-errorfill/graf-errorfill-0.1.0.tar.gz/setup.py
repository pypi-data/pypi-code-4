#!/usr/bin/env python
# coding=utf-8
"""
graf-errorfill

Graf plugin for add `errorfill` plot function

(C) 2013 hashnote.net, Alisue
"""
name = 'graf-errorfill'
version = '0.1.0'
author = 'Alisue'
author_email = 'lambdalisue@hashnote.net'

import os
from setuptools import setup, find_packages

setup(
    name=name,
    version=version,
    description = "",
    long_description=__doc__,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords = "graf",
    author = author,
    author_email = author_email,
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
        'mpltools>=0.2dev',
    ],
    dependency_links = [
        'http://github.com/tonysyu/mpltools/tarball/master#egg=mpltools-0.2dev'
    ],
    entry_points={
        'graf.plugins': [
            'errorfill = graf.builtins.errorfill:errorfill',
        ],
    },
)

