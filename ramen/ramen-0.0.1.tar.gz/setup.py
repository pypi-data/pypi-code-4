#!/usr/bin/env python

import os

try:
    from setuptools import setup, Extension, Command
except ImportError:
    from distutils.core import setup, Extension, Command


dependencies = ['motor', 'tornado']

setup(
    name='ramen',
    version='0.0.1',
    description="Tornado based simple web framework",
    long_description=open('README.md').read(),
    author='Anton Gorskiy',
    author_email='gorskiy.anton@gmail.com',
    url='http://gorskiy.kz/ramen',
    packages=['ramen'],
    license='Apache v2',
    install_requires=dependencies,
    scripts = ['ramen/bin/ramen'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers'
    ]
)
