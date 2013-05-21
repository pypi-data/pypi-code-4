#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sancta_article

setup(
    name     = 'sancta_article',
    version  = sancta_article.__version__,
    packages = find_packages(),
    requires = ['python (>= 2.5)'],
    description  = 'article tools',
    long_description = open('README.txt').read(),
    author       = 'Valeriy Semenov',
    author_email = 'valery.ravall@gmail.com',
    url          = 'https://github.com/Ravall/sancta_article.git',
    download_url = 'https://github.com/Ravall/sancta_article/tarball/master',
    license      = 'MIT License',
    keywords     = '',
    classifiers  = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
