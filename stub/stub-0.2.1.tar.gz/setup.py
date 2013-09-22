#!/usr/bin/python

from setuptools import setup, find_packages
from stub import __version__

setup(
	name='stub',
	version=__version__,
	packages=['stubbing'],
	py_modules=['stub'],
	author='Iain Lowe',
	author_email='iain.lowe@gmail.com',
	description='Temporarily modify callable behaviour and object attributes.',
	license='MIT',
	url='https://bitbucket.org/ilowe/stub',
	test_suite='stubtests',
	keywords='test testing stub mock virtual simulate decorate',
	test_requires=['byteplay'],
	install_requires=['byteplay']
)
