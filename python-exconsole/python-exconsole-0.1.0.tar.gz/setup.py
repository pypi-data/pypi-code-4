#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='python-exconsole',
    version='0.1.0',
    install_requires=[
    ],
    description='Emergency/postmortem Python console',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='https://github.com/Eugeny/exconsole',
    packages=find_packages(exclude=['*test*']),
)
