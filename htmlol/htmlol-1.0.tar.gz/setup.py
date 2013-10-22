#!/usr/bin/python3
# -*- coding: utf-8

from __future__ import print_function
import sys

if sys.version_info[0] < 3:
	print('Cannot run setup.py: Python 3.0 or greater is required', file = sys.stderr)
	sys.exit(1)

from distutils.core import setup

setup(
    name = 'htmlol',
    version = '1.0',
    description = 'Structured HTML builder and formatter',
    author = 'Murarth',
    author_email = 'Murarth@gmail.com',
    packages = ['htmlol'],
)
