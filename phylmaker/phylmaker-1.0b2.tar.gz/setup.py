#!/usr/bin/env python
import os
import setuptools

# Fetch __version__ information
ver_file = os.path.join(os.path.dirname(__file__), 'phylmaker', '__version__.py')
with open(ver_file) as f:
	exec(f.read())

# NB. Requires Python 2.6+
setuptools.setup(
		name='phylmaker',
		version=__version__,
		description='A Pythonic wrapper for the FileMaker Server XML API/interface',
		url='https://bitbucket.org/Raumkraut/phylmaker',
		author='Mel Collins',
		author_email='mel@raumkraut.net',
		license='MIT License',
		platforms = ["OS Independent"],
		packages=['phylmaker'],
		classifiers=[
				'Development Status :: 4 - Beta',
				'Intended Audience :: Developers',
				'License :: OSI Approved :: MIT License',
				'Operating System :: OS Independent',
				'Programming Language :: Python',
				'Topic :: Database :: Front-Ends',
				],
		install_requires=[
				'requests>=1.0',
				],
		)
