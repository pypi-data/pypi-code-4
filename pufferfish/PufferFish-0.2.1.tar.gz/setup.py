#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2011 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from setuptools import setup

setup(
    name='PufferFish',
    author='Giacomo Bagnoli',
    version = ':versiontools:pufferfish:',
    author_email='g.bagnoli@asidev.com',
    packages=['pufferfish'],
    include_package_data = True,
    url='http://code.asidev.net/pufferfish/',
    license='LICENSE.txt',
    description='SQLAlchemy session extension',
    long_description=open('README.txt').read(),
    install_requires=("SQLAlchemy < 0.8", "python-magic >= 0.4.0"),
    test_suite=('tests'),
    tests_require=("Nose", "coverage"),
    setup_requires=('versiontools >= 1.8',),
    classifiers  = [
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
