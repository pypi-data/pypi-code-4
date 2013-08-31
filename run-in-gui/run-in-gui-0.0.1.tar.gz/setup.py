#!/usr/bin/env python

from setuptools import setup
import os

dir = os.path.dirname(__file__)
path_to_main_file = os.path.join(dir, "src/runingui/__init__.py")
path_to_readme = os.path.join(dir, "README.md")
for line in open(path_to_main_file):
	if line.startswith('__version__'):
		version = line.split()[-1].strip("'").strip('"')
		break
else:
	raise ValueError, '"__version__" not found in "src/runingui/__init__.py"'
readme = open(path_to_readme).read(-1)

classifiers = [
'Development Status :: 4 - Beta',
'Environment :: Console',
'Environment :: No Input/Output (Daemon)',
'Intended Audience :: End Users/Desktop',
'Intended Audience :: System Administrators',
'License :: OSI Approved :: GNU General Public License (GPL)',
'Operating System :: POSIX :: Linux',
'Programming Language :: Python :: 2 :: Only',
'Programming Language :: Python :: 2.7',
]

setup(
	name = 'run-in-gui',
	version=version,
	description = 'Tools to run (possibly graphical) programs in logged-in user sessions on modern Linux distributions',
	long_description = readme,
	author='Manuel Amador (Rudd-O)',
	author_email='rudd-o@rudd-o.com',
	license="GPL",
	url = 'http://github.com/Rudd-O/run-in-gui',
	package_dir=dict([
					("runingui", "src/runingui"),
					]),
	classifiers = classifiers,
	packages = ["runingui"],
	scripts = ["bin/run-in-gui", 'bin/run-in-env-of'],
	keywords = "cron loginctl daemon GUI",
	zip_safe=False,
)
