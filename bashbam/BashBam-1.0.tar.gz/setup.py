#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='BashBam',
	description='',
    version='1.0',
    author='A.J. May',
    url='http://thegoods.aj7may.com/bashbam',
    packages=find_packages(),
    requires=['requests'],
    install_requires=['requests'],
    entry_points = {
        'console_scripts': ['bam = bashbam.views:main']
    },
    license="Creative Commons Attribution-ShareAlike 3.0 Unported License",
    zip_safe = False,
    include_package_data=True,
)