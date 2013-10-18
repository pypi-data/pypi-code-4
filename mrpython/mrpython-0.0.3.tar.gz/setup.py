# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
	name="mrpython",
	version="0.0.3",
	url='http://github.com/petermelias/mrpython',
	license='MIT',
	author='Peter M. Elias',
	author_email='petermelias@gmail.com',
	description='Collection of things for Python that dont warrant their own libraries.',
	packages=find_packages(),
	install_requires=[],
	extras_require={
		'test': ['nose', 'coveralls']
	},
	classifiers=[
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)