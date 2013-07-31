#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
* Date: 29.07.13
* Time: 18:56
* Original filename: 
"""

from __future__ import absolute_import, print_function
import optdict

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_description="""
<h1>OptDict</h1>

<p>Python module for easy to use command line options. With validation options
values and configuration from JSON file.</p>

<h2>Validations</h2>

<p>
The module provides this validators:
  <ul>
    <li> RequireAll(func1[, func2, ... funcN]) {synonym: Require}</li>
    <li> RequireOnce(func1[, func2, ... funcN])</li>
    <li> ValidAll(name1[, name2 ... nameN]) {synonym: Valid}</li>
    <li> ValidOnce(name1[, name2 ... nameN])</li>
    <li> Conflict(name1[, name2 ... nameN])</li>
    <li> ValidationQueue(Validator0[, Validator1])</li>
  </ul>
</p>
"""

setup(name='OptDict',
      version=optdict.__version__,
      author=optdict.__author__,
      author_email='me@mosquito.su',
      license="MIT",
      summary="OptDict module",
      description="OptDict - Option parser from dictionary, with configure from file and validation.",
      platform="all",
      url="http://github.com/mosquito/optdict",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          "Programming Language :: Python",
      ],
      long_description=long_description,
      packages=[
          'optdict',
      ],
)