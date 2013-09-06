#!/usr/bin/env python
# encoding=utf-8

"""Pythonic Setup for mucket."""


from setuptools import setup


setup(
    version='0.0.1',
    name='mucket',
    description='Mock whole S3 buckets',
    author=u'Jökull Sólberg Auðunsson',
    author_email='jokull@solberg.is',
    license='See LICENSE.',
    url='https://github.com/plain-vanilla-games/mucket',
    packages=['mucket'],
    install_requires=['httpretty>=0.6.3'],
)
