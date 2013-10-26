#!/usr/bin/env python3
from distutils.core import setup

'''
	(c) 2012 Christoph Grenz <christophg@grenz-bonn.de>
	This file is part of python-hiddev.

	python-hiddev is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	python-hiddev is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with python-hiddev.  If not, see <http://www.gnu.org/licenses/>.
'''

setup(
	name = 'HIDDev',
	version='0.4.1',
	description='Linux HIDDEV Python Bindings',
	author='Christoph Grenz',
	author_email='christophg+python@grenz-bonn.de',
	url='https://gitorious.org/python-hiddev/',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Environment :: X11 Applications :: Qt',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
		'Topic :: System :: Hardware :: Hardware Drivers',
	],
	data_files=[
		('share/applications', ['hiddevexplorer.desktop']),
	],
	packages = ['hiddev'],
	scripts = ['hiddevexplorer']
)
