import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "pyjath",
	version = "0.0.6",
	author = "Dan Newcome",
	author_email = "dan@dnuke.com",
	description = ("Template based xml to python data structure conversion."),
	license = "BSD",
	keywords = "xml",
	url = "http://packages.python.org/pyjath",
	packages=['pyjath'],
	long_description = read('README'),
	install_requires = ['lxml'],
	classifiers = [
		"Development Status :: 3 - Alpha",
		"Topic :: Software Development :: Libraries",
		"License :: OSI Approved :: BSD License",
	],
)
