# coding: utf-8
from setuptools import setup
import sys

if sys.version_info < (3,2):
	sys.stdout.write("At least Python 3.2 is required.\n")
	sys.exit(1)

__version__ = '1.1.1'

setup(
	name = 'pancake',
	version = __version__,
	author = 'Corinna Ernst',
	author_email = 'corinna.ernst@uni-due.de',
	description = 'A Data Structure for Pangenomes -- Identification of Singletons and Core Regions Dependent on Pairwise Sequence Similarities',
	#long_description = "Non-databse approach for identification of singletons and core regions in arbitrary sequence sets dependent on pairwise sequence similarities (as provided by common sequence alignment tools), and independent of annotation data.'),
	license = 'MIT',
	url = 'https://bitbucket.org/CorinnaErnst/pancake',
	packages = ['pancake'],
	scripts = ['bin/pancake'],
	install_requires=["numpy", "biopython"],
	test_suite = 'nose.collector',
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Bio-Informatics"
	]
)
