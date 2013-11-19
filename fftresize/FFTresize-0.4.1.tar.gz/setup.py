#!/usr/bin/env python2

from distutils.core import setup

from fftresize import fftresize


_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: ISC License (ISCL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Topic :: Multimedia :: Graphics',
]

with open('README.rst', 'r') as file:
    _long_description = file.read()

_setup_args = {
    'author':           fftresize.__author__,
    'author_email':     fftresize.__email__,
    'classifiers':      _classifiers,
    'description':      fftresize.__doc__,
    'license':          fftresize.__license__,
    'long_description': _long_description,
    'name':             'FFTresize',
    'url':              'https://code.google.com/p/fftresize',
    'version':          fftresize.__version__,
}


if __name__ == '__main__':

    setup(packages=['fftresize'], scripts=['scripts/fftresize'],
          **_setup_args)
