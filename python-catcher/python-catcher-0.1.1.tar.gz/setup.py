#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='python-catcher',
    version='0.1.1',
    install_requires=[
        'requests'
    ],
    description='Beautiful stack traces for Python',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(exclude=['*test*']),
)
