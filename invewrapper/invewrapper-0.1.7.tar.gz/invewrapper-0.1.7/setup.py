#! /usr/bin/env python

from setuptools import setup
import invewrapper

setup(
	name='invewrapper',
	version='0.1.7',
	description='dummy/transitional package that depends on "pew"',
    long_description='https://pypi.python.org/pypi/pew',
	author='Dario Bertini',
	author_email='berdario+pypi@gmail.com',
	install_requires=['pew']
)
