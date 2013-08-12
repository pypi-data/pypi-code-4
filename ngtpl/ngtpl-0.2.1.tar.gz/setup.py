#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='ngtpl',
    version='0.2.1',
    description='Collect angular templates, outputs compiled html',
    #long_description=read('README.rst'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='http://github.com/mbr/ngtpl',
    license='MIT',
    packages=find_packages(exclude=['test']),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ngtpl = ngtpl:main',
        ],
    }
)
