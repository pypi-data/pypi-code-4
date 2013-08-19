import os
from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
	namespace_packages = ['tiddlywebplugins'],
	name = 'tiddlywebplugins.mapuser',
	version = VERSION,
	description = 'Allows TiddlyWeb users to create alias usernames, deliberately without validation.',
	long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
	author = 'Ben Paddock',
	url = 'http://pypi.python.org/pypi/tiddlywebplugins.mapuser',
	packages = find_packages(exclude=['test']),
	author_email = 'pads@thisispads.me.uk',
	platforms = 'Posix; MacOS X; Windows',
	install_requires = ['tiddlyweb'],
	extras_require = {
		'testing': ['pytest', 'httplib2', 'wsgi_intercept'],
		'coverage': ['pytest-cov', 'python-coveralls'],
		'code': ['flake8']
	},
	zip_safe = False,
	)
