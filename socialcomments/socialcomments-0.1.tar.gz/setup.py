#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'socialcomments',
	version = '0.1',
	description = 'Let users post comments via Facebook, Twitter and LinkedIn',
	author = 'Mark Steadman',
	author_email = 'marksteadman@me.com',
	url = 'https://github.com/mrmarksteadman/social-comments',
	install_requires = [
		'Django>=1.4',
		'bambu-tools>=3.0.3'
	],
	packages = [
		'socialcomments',
		'socialcomments.migrations',
		'socialcomments.providers',
		'socialcomments.templatetags'
	],
	package_data = {
		'socialcomments': [
			'templates/socialcomments/*.*',
			'templates/socialcomments/form/*.*'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)