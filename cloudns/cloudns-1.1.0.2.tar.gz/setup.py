#!/usr/bin/env python
# coding=utf-8

"""
python distribute file
"""

from setuptools import setup, find_packages

# make sure I can import cloudns without installing any dependency, otherwise,
# this won't work.
from cloudns import __version__

setup(
    name="cloudns",
    version=__version__,
    packages=find_packages(),
    install_requires=['requests>=1.1.0'],
    author="Yuanle Song",
    author_email="g-yygame-brd@yy.com",
    maintainer="Yuanle Song",
    maintainer_email="g-yygame-brd@yy.com",
    description="YY cloudns API python client",
    long_description=open('README.rst').read(),
    license="Artistic License or GPLv2+",
    url="https://pypi.python.org/pypi/cloudns",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Artistic License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3'
    ]
)
