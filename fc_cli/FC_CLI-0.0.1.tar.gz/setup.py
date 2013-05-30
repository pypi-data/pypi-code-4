#!/usr/bin/env python

from setuptools import setup

setup(name='FC_CLI',
      version='0.0.1',
      description='Get a FullContact report on somebody, and store it in Cloudant',
      author='Max Thayer',
      author_email='garbados@gmail.com',
      url='https://github.com/garbados/fc_cli',
      packages=['fc_cli'],
      test_suite="test"
      )