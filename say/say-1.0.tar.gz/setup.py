#! /usr/bin/env python
from setuptools import setup
import sys


def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.split() ]
    
    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.

setup(
    name='say',
    version="1.0",
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Super-simple templated printing. E.g.: say("Hello, {whoever}!", indent=1)',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/say',
    packages=['say'],
    install_requires=['six', 'options>=0.5', 'stuf>=0.9.12', 'simplere>=1.0'],
    tests_require = ['tox', 'pytest', 'six'],
    zip_safe = True,
    keywords='print format template interpolate say',
    classifiers=linelist("""
        Development Status :: 4 - Beta
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Libraries :: Python Modules
        Topic :: Printing
    """)
)
