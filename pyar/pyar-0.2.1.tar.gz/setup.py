#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

from setuptools import setup, find_packages
from pyar.version import __version__

PACKAGE      = "pyar"
NAME         = "pyar"
DESCRIPTION  = "pyar sqlhelper based sqlbuilder."
AUTHOR       = "Jefurry"
AUTHOR_EMAIL = "jefurry@qq.com"
URL          = "http://www.penqie.com"
VERSION      = __version__#__import__(PACKAGE).__version__

setup(name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	keywords="pyar sqlwrapper sqlhelper",
	dependency_links=[],
	install_requires=["DBUtils", "sqlbuilder"],
	url=URL,
	license="LGPL",
	packages=[PACKAGE] + find_packages(),
	scripts=["pyar/scripts/test.py"],)
