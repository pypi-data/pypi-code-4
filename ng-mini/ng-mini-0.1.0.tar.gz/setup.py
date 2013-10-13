#!/usr/bin/python
from setuptools import setup , find_packages

setup(
        name = 'ng-mini',
        version = '0.1.0',
        long_description=open("README.md").read(),
        packages = find_packages(),
        requires = ['bottle','PyYAML'],
        author = 'qing.chen',
        url = 'http://www.chenqing.org'
        )
