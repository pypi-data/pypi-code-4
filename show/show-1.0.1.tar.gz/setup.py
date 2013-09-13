#! /usr/bin/env python
from setuptools import setup
import sys, platform

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.strip() ]

    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.

system = str(sys.platform).lower()
impl = platform.python_implementation()

install_requires = ['six>=1.4.1', 'options>=1.0', 'say>=1.0', 'stuf>=0.9.12',
                    'mementos>=1.0', 'codegen', # 'astor'
                    ]

if 'darwin' in system:
    if impl != 'PyPy':
        install_requires += ['readline']

        # if iPython ran under PyPy, it'd require readline too
        # but on my system, readline fails to install under PyPy
        # thus this spot omission

elif 'win32' in system:
    install_requires += ['pyreadline']


setup(
    name='show',
    version='1.0.1',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Debug print statements, done right. E.g. show(x)',
    long_description=open('README').read(),
    url='https://bitbucket.org/jeunice/show',
    packages=['show'],
    install_requires=install_requires,
    tests_require = ['tox', 'pytest', 'six>=1.4.1'],
    zip_safe = False,
    keywords='debug print display show',
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
        Topic :: Software Development :: Debuggers
    """)
)
