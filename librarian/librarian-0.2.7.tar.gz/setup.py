#!/usr/bin/python
from setuptools import setup, find_packages

__version__ = '0.2.7'
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
SOURCE = 'librarian'
TESTDIR = 'test'
PROJECTNAME = 'librarian'
PROJECTSITE = 'nekroze.eturnilnetwork.com'
PROJECTDESC = 'Python advanced card game library.'
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
    install_requires = ['six>=1.3.0'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    **kwds
)
