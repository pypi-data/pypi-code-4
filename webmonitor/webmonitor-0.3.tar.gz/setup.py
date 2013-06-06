#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='webmonitor',
    version='0.3',
    description=('Monitors a website by retrieving it periodically, '
                 'complains if its down.'),
    long_description=read('README.rst'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='http://github.com/mbr/webmonitor',
    license='MIT',
    py_modules=['webmonitor'],
    install_requires=['logbook', 'requests'],
    entry_points={
        'console_scripts': [
            'webmonitor = webmonitor:main',
        ],
    }
)
