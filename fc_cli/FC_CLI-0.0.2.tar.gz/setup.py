#!/usr/bin/env python

from setuptools import setup

setup(name='FC_CLI',
      version='0.0.2',
      description='Get a FullContact report on somebody, and store it in Cloudant',
      author='Max Thayer',
      author_email='garbados@gmail.com',
      url='https://github.com/garbados/fc_cli',
      packages=['fc_cli'],
      entry_points={
          'console_scripts': [
              'fc_cli = fc_cli.__init__:main',
          ],
      },
      test_suite="test"
      )