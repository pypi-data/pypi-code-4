'''
---------------------------------------------------------
common.ngSeqUtils_setup.py
---------------------------------------------------------

This is the :py:class:`setuptools` setup file for python package 
distribution. It will install all utility scripts and module for Next Generation
Sequencing data.

usage: python ngSeqUtils_setup.py install

.. moduleauthor:: Nick Schurch <nschurch@dundee.ac.uk>

:module_version: 1.0
:created_on: 2013-07-08
'''
import os, ez_setup
ez_setup.use_setuptools()

from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name = 'ngSeqUtils',
      version = '1.0',
      description = '',
      author  = 'Nick Schurch',
      author_email = 'nschurch@dundee.ac.uk',
      license = 'CCBY',
      
      scripts=['ngseq/switchStrand.py'],
      packages=['script_options', 'script_logging', 'tests'],      
      
      keywords = "Next Generation Sequencing BAM",
      url = "",
      long_description=read('ngseq/README.txt'),
      classifiers=[
                   "Programming Language :: Python :: 2.6",
                   "Development Status :: 3 - Alpha",
                   "Topic :: Scientific/Engineering :: Bio-Informatics",
                   "License :: Other/Proprietary License",
                   ],
      install_requires = ['sys', 'os', 'logging', 'pysam'],
      )


