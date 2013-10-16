#!/usr/bin/env python
# coding=utf-8
"""
graf-plugin-skeleton

Graf plugin skeleton

(C) 2013 hashnote.net, Alisue
"""
name = 'graf-plugin-skeleton'
version = '0.1.0'
author = 'Your name'
author_email = 'Your email'

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
    #url=r"",
    #download_url =r"",
    #license = 'MIT',
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
            #'parsers.AnyParser = graf.plugins.parsers.any:AnyParser',
            #'loaders.AnyLoader = graf.plugins.loaders.any:AnyLoader',
            #'filters.any = graf.plugins.filters.any:any',
        ],
    },
)

