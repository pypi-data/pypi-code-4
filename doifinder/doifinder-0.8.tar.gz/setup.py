#!/usr/bin/env python

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import doifinder

setup(name='doifinder',
      version=doifinder.__version__,
      description='Python Distribution Utilitie to retrive a DOI number from Crossref, according to a given metadata',
      author='SciELO',
      author_email='scielo-dev@googlegroups.com',
      maintainer="Fabio Batalha",
      maintainer_email="fabio.batalha@scielo.org",
      license="BSD License",
      url='http://www.python.org/sigs/distutils-sig/',
      packages=['doifinder'],
      package_data={'': ['README.rst', 'HISTORY.md', 'LICENSE']},
      package_dir={'doifinder': 'doifinder'},
      include_package_data=True,
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
