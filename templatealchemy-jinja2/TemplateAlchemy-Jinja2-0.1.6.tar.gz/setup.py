#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/07/03
# copy: (C) Copyright 2013 Cadit Inc., see LICENSE.txt
#------------------------------------------------------------------------------

import os, sys, re
from setuptools import setup, find_packages

# require python 2.7+
assert(sys.version_info[0] > 2
       or sys.version_info[0] == 2
       and sys.version_info[1] >= 7)

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

test_requires = [
  'nose                 >= 1.2.1',
  'coverage             >= 3.5.3',
  ]

requires = [
  'TemplateAlchemy      >= 0.1.18',
  'jinja2               >= 2.7',
  'MarkupSafe           >= 0.18',
  ]

setup(
  name                  = 'TemplateAlchemy-Jinja2',
  version               = '0.1.6',
  description           = 'Provides the Jinja2 template rendering engine to `TemplateAlchemy`',
  long_description      = README,
  classifiers           = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'License :: Public Domain',
    ],
  author                = 'Philip J Grabner, Cadit Health Inc',
  author_email          = 'oss@cadit.com',
  url                   = 'http://github.com/cadithealth/templatealchemy-jinja2',
  keywords              = 'templatealchemy jinja2 driver',
  packages              = find_packages(),
  namespace_packages    = ['templatealchemy_driver'],
  include_package_data  = True,
  zip_safe              = True,
  install_requires      = requires,
  tests_require         = test_requires,
  test_suite            = 'templatealchemy',
  entry_points          = '',
  license               = 'MIT (http://opensource.org/licenses/MIT)',
  )

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
