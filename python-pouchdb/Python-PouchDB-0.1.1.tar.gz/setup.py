#!/usr/bin/env python

from distutils.core import setup

setup(
	name="Python-PouchDB",
	version="0.1.1",
	description="A Python interface to PouchDB",
	long_description="""Python-PouchDB provides an interface to all the
goodness of the PouchDB JavaScript library (http://pouchdb.com/). It's
released under the Apache License v2 and it also offers a synchronous
API.

Uses QtWebKit internally, so either PySide or PyQt4 is required.""",
	author="Marten de Vries",
	author_email="marten@openteacher.org",
	url="http://python-pouchdb.marten-de-vries.nl/",
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: JavaScript",
		"Programming Language :: Python :: 2 :: Only",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries",
	],
	packages=["pouchdb"],
	package_data={
		"pouchdb": [
			"data/bridge.html",
			"data/pouchdb-nightly.js",
		]
	},
)
