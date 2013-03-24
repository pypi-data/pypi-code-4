#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='arpy',
		version='1.0.0',
		description='Library for accessing "ar" files',
		author=u'Stanisław Pitucha',
		author_email='viraptor@gmail.com',
		url='http://bitbucket.org/viraptor/arpy',
		py_modules=['arpy'],
		license="Simplified BSD",
		test_suite='test',
		long_description="""'arpy' is a library for accessing the archive files and reading the contents. It supports extended long filenames in both GNU and BSD format. Right now it does not support the symbol tables, but can ignore them gracefully.

Usage instructions are included in the module docstring. Works with python >=2.6 and >=3.3.""",
		classifiers=[
			"Development Status :: 5 - Production/Stable",
			"License :: OSI Approved :: BSD License",
			"Programming Language :: Python :: 2.6",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3.3",
			"Topic :: System :: Archiving",
			]
		)

