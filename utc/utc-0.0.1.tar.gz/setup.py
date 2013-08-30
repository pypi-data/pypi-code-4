#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='utc',
    version='0.0.1',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://bits.btubbs.com/utc',
    description='A tiny library for working with UTC time.',
    long_description=open('README.rst').read(),
)
