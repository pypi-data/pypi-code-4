#!/usr/bin/env python
from distutils.core import setup

with open('README.md') as file:
        long_description = file.read()

setup(
   name = 'graphitesend',
   version = '0.0.5',
   description = 'A simple interface for sending metrics to Graphite',
   author = 'Danny Lawrence',
   author_email = 'dannyla@linux.com',
   url = 'https://github.com/daniellawrence/graphitesend',
   package_dir = {'': 'src'},
   packages = [''],
   scripts = ['bin/graphitesend'],
   long_description = long_description
 )
