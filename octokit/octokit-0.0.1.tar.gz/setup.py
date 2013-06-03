#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from octokit import VERSION

setup(name = 'octokit',
      version = VERSION,
      keywords = ('octokit', 'github', 'api'),
      description = 'Simple Python wrapper for the GitHub API',
      long_description = 'Simple Python wrapper for the GitHub API',
      license = 'MIT License',

      url = 'https://github.com/liluo/octokit.py',
      author = 'liluo',
      author_email = 'i@liluo.org',

      packages = ['octokit'],
      include_package_data = True,
      install_requires = [],
      classifiers = [],
      )
