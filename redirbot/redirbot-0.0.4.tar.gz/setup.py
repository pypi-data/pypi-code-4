#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from redirbot import __version__

setup(
    name='redirbot',
    version=__version__,
    description='IRCBot, telling people they should contact you on different nickname',
    author='Jan Matejka',
    author_email='yac@blesmrt.net',
    url='https://github.com/yaccz/redirbot',

    packages = find_packages(
        where = '.'
    ),

    install_requires = [
        "setuptools",
        "twisted>=11.1.0",
        "argparse",
    ],

    package_data = {
        "redirbot": [ "data/*/*" ]
    },

    entry_points = {
        'console_scripts': ['redirbot = redirbot:main']},

     classifiers=[
        "Operating System :: POSIX",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Framework :: Twisted",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Environment :: No Input/Output (Daemon)",
        "Natural Language :: English",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
    ],
)
