#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import nodist

setup(
    name='nodist',
    version=nodist.__version__,
    packages=['nodist'],
    license='GNU General Public License, version 2',
    scripts=['scripts/nodist'],
    url='https://github.com/keremc/nodist',
    author='Kerem Çakırer',
    author_email='kcakirer@hotmail.com',
    long_description=open("README").read(),
    description='Node.js version manager',
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Topic :: Utilities"
        ]
    )
