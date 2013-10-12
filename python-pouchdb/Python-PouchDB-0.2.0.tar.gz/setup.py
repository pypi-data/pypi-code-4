#!/usr/bin/env python

from setuptools import setup
import pouchdb
import os

def find_package_data():
	os.chdir("pouchdb")
	for root, dirs, files in os.walk("data"):
		yield os.path.join(root, "*.js")
	os.chdir("..")

setup(
	name="Python-PouchDB",
	version=pouchdb.__version__,
	description="A Python interface to PouchDB",
	long_description="""Python-PouchDB provides an interface to all the
goodness of the PouchDB JavaScript library (http://pouchdb.com/). It's
released under the Apache License v2 and it also offers a synchronous
API.

Uses QtWebKit internally, so either PySide or PyQt4 is required.""",
	author=pouchdb.__author__,
	author_email="marten@openteacher.org",
	url="http://python-pouchdb.marten-de-vries.nl/",
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: JavaScript",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries",
	],
	packages=["pouchdb"],
	package_data={
		"pouchdb": ["data/bridge.html"] + list(find_package_data()),
	},
	test_suite="pouchdb.tests",
	use_2to3=True,
)
