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


def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.split() ]
    
    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.

setup(
    name='mementos',
    version="1.0",
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Memoizing metaclass. Drop-dead simple way to create cached objects',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/mementos',
    py_modules=['mementos'],
    install_requires=[],
    tests_require = ['tox', 'pytest'],
    zip_safe = True,
    classifiers=linelist("""
        Development Status :: 5 - Production/Stable
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.5
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)
