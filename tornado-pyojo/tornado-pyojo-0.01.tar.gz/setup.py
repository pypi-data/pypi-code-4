#!/usr/bin/env python

from distutils.core import setup
from pyojo import __version__

setup(name='tornado-pyojo',
	version=__version__,
	description="Tornado even easier!",
	author='Leandro Brunner',
	author_email='leandrobrunner@yahoo.com.ar',
	url='http://tornado-pyojo.com.ar/',
	download_url='http://tornado-pyojo.com.ar/downloads/pyojo-tornado.tar.gz',
	keywords=('pyojo', 'tornado', 'framework', 'web'),
	packages=['pyojo', 'pyojo.web'],
	long_description="""Simple modular applications and functions that make easy you job.
	Aplicaciones modulares simples y funciones que facilitan tu trabajo""",
	license="Public domain",
	platforms=["any"],
	requires=['tornado (>=2.3)'],
	)
