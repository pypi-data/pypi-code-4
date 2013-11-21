#!/usr/bin/python
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "RuSocSci",
	version = "0.6.6",
	install_requires = "pyserial",
	author = "Wilbert van Ham",
	author_email = "W.vanHam@socsci.ru.nl",
	description = "Support package for Radboud University Nijmegen, "\
			"Faculty of Social Sciences hardware, with PsychoPy-like API.",
	license = "GPLv3+",
	keywords = "hardware",
	url = "http://www.socsci.ru.nl/~wilberth/python/hardware.html",
	packages=['rusocsci'],
	long_description=read('README'),
	classifiers=[
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
	],
)
