#!/usr/bin/env python
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'protoweb'))

version = '-1'

try:
    from setuptools import setup
    import protoweb
    version = protoweb.__version__
except ImportError:
    from distutils.core import setup


def get_long_description():
    return """protoweb is a simple, yet useful tool for anyone who wants \
to develop quicky on top of cyclone (or probably tornado, as it is easy to \
fork and implement), with Less support (you have to install nodejs and the \
less compiler. For now, it's just this!"""

extra = dict(
    scripts=["bin/protoweb"],
    install_requires=["cyclone"]
)

setup(
    name="protoweb",
    license="http://opensource.org/licenses/MIT",
    version=version,
    description="a very simple Cyclone web development mock tool",
    keywords="python cyclone web development mock",
    long_description=get_long_description(),
    author="Richard Kuesters",
    author_email="rkuesters@gmail.com",
    url="https://github.com/vltr/protoweb",
    packages=[
        "protoweb",
        "protoweb.fs",
        "protoweb.processors",
        "protoweb.server",
        "protoweb.util"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    **extra)
