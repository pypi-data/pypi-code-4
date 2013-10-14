# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
	name='assetman',
	version='0.0.2',
	url='http://github.com/petermelias/assetman',
	license='BSD',
	author='Peter M. Elias',
	author_email='petermelias@gmail.com',
	description='Generic blob-data asset manager that provides an API, CLI interface, for managing S3 assets and the respective CloudFront delivery setup.',
	long_description=__doc__,
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	platforms='any',
	install_requires=[
		'boto',
	],
	extras_require={
		'test': ['nose', 'wand', 'coveralls']
	},
	classifiers=[
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],
)