#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

from setuptools import setup, find_packages

setup(name="pyar",
	version="0.0.3",
	description="pyar",
	author="Jefurry",
	author_email="jefurry@qq.com",
	keywords="pyar sqlwrapper sqlhelper",
	dependency_links=[],
	install_requires=["DBUtils", "sqlbuilder"],
	url="http://www.penqie.com",
	license="LGPL",
	packages=["pyar"] + find_packages(),
	scripts=["pyar/scripts/test.py"],)
