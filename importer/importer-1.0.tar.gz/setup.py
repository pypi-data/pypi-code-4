#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    keen importer: setup script
'''

# distutils
from setuptools import setup


setup(name="importer",
      version="1.0",
      description="Data transfer tool for analytics providers",
      author="Sam Gammon",
      author_email="sam@keen.io",
      url="https://github.com/keen-labs/Keen-Importer",
      packages=["importer", "importer_tests"],
      install_requires=["mixpanel", "keen"],
      tests_require=["nose"]
)
