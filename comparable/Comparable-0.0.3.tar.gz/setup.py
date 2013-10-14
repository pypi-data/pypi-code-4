#!/usr/bin/env python

"""
Setup script for Comparable.
"""

import setuptools

from comparable import __project__


setuptools.setup(
    name=__project__,
    version='0.0.3',

    description="Base class to enable objects to be compared for similarity.",
    url='http://pypi.python.org/pypi/Comparable',
    author='Jace Browning',
    author_email='jace.browning@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=open('README.rst').read(),
    license='LGPL',

    install_requires=[],
)
