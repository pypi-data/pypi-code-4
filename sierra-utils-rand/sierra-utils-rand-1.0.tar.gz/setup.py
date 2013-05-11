#!/usr/bin/env python

from distutils.core import setup

long_description = '''
Use this package to generate random strings and more (only random strings for now, btw...)

Documentation on http://github.com/rafaelsierra/sierra-utils-rand
''' 

setup(name='sierra-utils-rand',
      version='1.0',
      description='Utility increase your options with random functions',
      long_description=long_description,
      author='Rafael Sierra',
      author_email='sierra@rafaelsdm.com',
      url='http://github.com/rafaelsierra/sierra-utils-rand',
      packages=[
                'sierra',
                'sierra.utils',
                ],
      package_dir = {'':'src'},
      license = 'MIT',
)
