#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='MoshPit',
	description='A wrapper for mosh.  Save hosts and connect to them by nickname.',
    version='2.1',
    author='A.J. May',
    url='http://moshpit.aj7may.com',
    packages=find_packages(),
    requires=['SQLAlchemy(>0.8.0)'],
    install_requires=['SQLAlchemy>0.8.0'],
    scripts=['bin/pit'],
    license="Creative Commons Attribution-ShareAlike 3.0 Unported License",
    zip_safe = False,
    include_package_data=True,
)