#!/usr/bin/env python

from distutils.core import setup

setup(
	name = "epubC",
	version = "0.2",
	description = ".epub file creator",
	author = "Awad Mackie",
	author_email = "firesock.serwalek@gmail.com",
	py_modules = ["epubC"],
	license = "GPLv3",
	url = "https://bitbucket.org/firesock/epubc/",
	long_description = """\
	epubC.py - .epub file creator
	=============================

        epub is an ebook file format by the IDPF
        (http://en.wikipedia.org/wiki/.epub). This library provides
        classes to pack XHTML content together into a .epub file version 2.0.

	- Requires lxml - checked with 3.0.1
	- Works with Python 3.2.5""",
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Topic :: Software Development :: Libraries :: Python Modules"],
	keywords = ["epub", "ebook"]
	)
