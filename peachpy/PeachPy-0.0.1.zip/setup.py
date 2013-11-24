#!/usr/bin/python

from peachpy import __version__
from distutils.core import setup

import os

root_path = os.path.dirname(__file__)

readme_filename = os.path.join(root_path, 'README.rst')
with open(readme_filename, 'r') as readme_file:
	readme_content = readme_file.read()

setup(
	name = "PeachPy",
	version = __version__,
	description = "Portable Efficient Assembly Codegen in Higher-level Python",
	author = "Marat Dukhan",
	author_email = "maratek@gmail.com",
	url = "https://bitbucket.org/MDukhan/peachpy/",
	packages = ['peachpy'],
	keywords = ["assembly", "codegen", "x86-64", "arm"],
	long_description = readme_content,
	requires = [],
	classifiers = [
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: BSD License",
		"Operating System :: OS Independent",
		"Programming Language :: Assembly",
		"Programming Language :: Python",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Natural Language :: English",
		"Topic :: Scientific/Engineering",
		"Topic :: Software Development",
		"Topic :: Software Development :: Assemblers",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Software Development :: Compilers",
		"Topic :: Software Development :: Libraries"
		])