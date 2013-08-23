#!/usr/bin/env python

import gitlab3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=gitlab3.__name__,
    version=gitlab3.__version__,
    license=gitlab3.__license__,
    description='GitLab API v3 Python Wrapper.',
    packages=['gitlab3'],
    author=gitlab3.__author__,
    author_email='alexvh@cs.columbia.edu',
    install_requires=['requests'],
    url='http://github.com/alexvh/python-gitlab3',
)
