#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from pointless import __version__

CLASSIFIERS = [
]

setup(
    name='py-pointless',
    version=__version__,
    description='this is pointless. do not install this.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Kim Thoenen',
    author_email='kim@smuzey.ch',
    url='https://github.com/chive/py-pointless',
    packages=find_packages(),
    license='MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)