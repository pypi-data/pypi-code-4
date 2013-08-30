#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import nodevers

setup(
    name='nodevers',
    version=nodevers.__version__,
    packages=['nodevers'],
    license='BSD (3-Clause) License',
    scripts=['scripts/nodevers'],
    url='https://github.com/keremc/nodevers',
    author='Kerem Çakırer',
    author_email='kcakirer@hotmail.com',
    long_description=open("README").read(),
    description='Node.js version manager',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Topic :: Utilities"
        ]
    )
