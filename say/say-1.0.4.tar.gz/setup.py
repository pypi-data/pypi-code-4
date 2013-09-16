#! /usr/bin/env python
from setuptools import setup
import sys
import os

_PY3 = sys.version_info[0] == 3

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.split() ]

    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.

def getmetadata(filepath):
    """
    Return a dictionary of metadata from a file, without importing it. This
    trick needed because importing can set off ImportError, in that setup.py
    runs by definition before the modules it sets up (or their dependencies) are
    available.
    """
    if _PY3:
        exec(open(filepath).read())
        return vars()
    else:
        execfile(filepath)
        return locals()

metadata = getmetadata('./say/version.py')

setup(
    name='say',
    version=metadata['__version__'],
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Super-simple templated printing. E.g.: say("Hello, {whoever}!", indent=1)',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/say',
    packages=['say'],
    install_requires=['six>=1.4.1', 'options>=1.0', 'stuf>=0.9.12', 'simplere>=1.0'],
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
