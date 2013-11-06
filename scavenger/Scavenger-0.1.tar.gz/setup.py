#!/usr/bin/env python
from distutils.core import setup

setup(
	name='Scavenger',
	version='0.1',
	description='Light redis search engine',
	author='Jared Patrick',
	author_email='jared.patrick@gmail.com',
	packages=['scavenger',],
	url='http://pypi.python.org/pypi/Scavenger/',
	license='LICENSE.txt',
	long_description=open('README.txt').read(),
	install_requires=[
		'django',
		'redis',
		'mongoengine',
	],
)