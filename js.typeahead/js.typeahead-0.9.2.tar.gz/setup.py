#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# setup
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-27


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)
                        # XXX: Don't put absolute imports in setup.py

import os, sys
from setuptools import setup, find_packages

# Import the version from the release module
project_name = 'js.typeahead'
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, 'js', 'typeahead'))
from release import VERSION as version

setup(name=project_name,
      version=version,
      description="Fanstatic Package of Twitter's Typeadhead.js",
      long_description=open(os.path.join("docs", "readme.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Development Status :: 5 - Production/Stable",
          "Topic :: Software Development :: Libraries"
      ],
      keywords='typeahead fanstatic',
      author='Merchise Autrement',
      author_email='',
      url='http://www.merchise.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['js', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'fanstatic>=0.16',
          'js.jquery>=1.9',
      ],
      entry_points="""
      [fanstatic.libraries]
      js.typeahead = js.typeahead:lib
      """,
      )
