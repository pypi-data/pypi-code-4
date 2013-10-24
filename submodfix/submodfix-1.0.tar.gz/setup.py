#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='submodfix',
	description='A tool to add submodules to a git repository from a .gitmodules file.',
    version='1.0',
    author='A.J. May',
    url='http://submodfix.aj7may.com',
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['submodfix = submodfix.submodfix:main']
    },
    license="Creative Commons Attribution-ShareAlike 3.0 Unported License",
    zip_safe = False,
    include_package_data=True,
)