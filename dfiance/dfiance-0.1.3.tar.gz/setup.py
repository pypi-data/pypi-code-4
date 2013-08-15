#!/usr/bin/env python

from distutils.core import setup

setup(
    name='dfiance',
    version='0.1.3',
    license='BSD',
    author="Daniel Lepage",
    author_email="dplepage@gmail.com",
    packages=['dfiance',],
    long_description=open('README.rst').read(),
    url='https://github.com/dplepage/dfiance',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
    ]
)