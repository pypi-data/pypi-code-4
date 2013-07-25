#!/usr/bin/env python

import os.path
import sys
from glob import glob


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


setup(
    name='DaemonCxt',
    version='1.5.6',
    description='Library to implement a well-behaved Unix daemon process',
    long_description=readme(),
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    url='https://github.com/ewiger/daemoncxt',
    license='PSF',
    packages=['daemoncxt', 'daemoncxt.version'],
    package_dir={
        'daemoncxt': 'src/daemoncxt',
    },
    download_url='https://github.com/ewiger/daemoncxt/tarball/master',
)

