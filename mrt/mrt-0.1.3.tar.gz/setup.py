#!/usr/bin/python

import os
import glob

from setuptools import setup

datadir = 'mrt/resources'
all_data_files = [ (root, [ os.path.join(root, f) for f in files ] ) for root, dirs, files in os.walk(datadir) ]

print "---"
print all_data_files
print "---"

setup(
   name = 'mrt',
   version = '0.1.3',
   url = "http://bitbucket.org/pieterb/mrt/",
   author = "Pieter B.",
   author_email = "pbu_mrt@zoho.com",
   description = "Mothur reporting tool",
   license = "BSD",
   keywords = "Mothur literate programming reproducible research",
   packages = ['mrt'],
   data_files = all_data_files,
   long_description = "Mothur reporting tool",
   entry_points = {
      'console_scripts': [
         'mrt = mrt.main:main',
         'mrt_hist_seq_length = mrt.mrt_hist_seq_length:main'
         ]
      },
   classifiers = [
      "Development Status :: 3 - Alpha",
      "Environment :: Console",
      "Intended Audience :: Science/Research",
      "License :: Public Domain",
      "Natural Language :: English",
      "Operating System :: POSIX :: Linux",
      "Programming Language :: Python",
      "Topic :: Scientific/Engineering :: Bio-Informatics",
      "Topic :: Software Development :: Documentation"
      ],
   install_requires=[
      "numpy",
      "matplotlib"
      ]
)
