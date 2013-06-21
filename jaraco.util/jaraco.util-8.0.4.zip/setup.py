# -*- coding: UTF-8 -*-

"""
Setup script for building jaraco.util distribution

Copyright © 2004-2013 Jason R. Coombs
"""

from __future__ import unicode_literals

import setuptools

name = 'jaraco.util'

setup_params = dict(
	# convert to bytes to work around UnicodeDecodeError when using bdist --formats gztar
	name = str(name),
	use_hg_version=True,
	description = 'General utility modules that supply commonly-used functionality',
	long_description = open('README').read(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://pypi.python.org/pypi/' + name,
	packages = setuptools.find_packages(exclude=['tests']),
	# convert to bytes to work around TypeError when installed with PIP
	# https://github.com/pypa/pip/issues/449
	namespace_packages = [str('jaraco')],
	license = 'MIT',
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
	],
	entry_points = {
		'console_scripts': [
			'roll-dice = jaraco.util.dice:do_dice_roll',
			'calc-prorate = jaraco.dateutil:calculate_prorated_values',
		],
	},
	install_requires=[
		'six>=1.3.0',
	],
	tests_require=[
		'pytest>=2',
		'mock',
	],
	setup_requires=[
		'hgtools',
		'pytest-runner',
	],
)

if __name__ == '__main__':
	setuptools.setup(**setup_params)
