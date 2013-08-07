#!/usr/bin/python
import re
import os
import sys
import platform
from setuptools import setup


__version__ = '0.1.2'
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
SOURCE = 'curator'
TESTDIR = 'test'
PROJECTNAME = 'librarian-curator'
PROJECTSITE = 'nekroze.eturnilnetwork.com'
PROJECTDESC = 'None'
PROJECTLICENSE = 'MIT'
PLATFORMS = ['any']

kwds = {}
kwds['version'] = __version__
kwds['description'] = PROJECTDESC
kwds['long_description'] = open('README.rst').read()
kwds['license'] = PROJECTLICENSE


setup(
    name=PROJECTNAME,
    author=__author__,
    author_email=__email__,
    url=PROJECTSITE,
    platforms=PLATFORMS,
    packages=[SOURCE],
    install_requires=['colorama>=0.2.5', 'librarian>=0.2.0'],
    entry_points={
        'console_scripts': [
            'curator = curator.driver:main',
            ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities"
    ],
    **kwds
)
