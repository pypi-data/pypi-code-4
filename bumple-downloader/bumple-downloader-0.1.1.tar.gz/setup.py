# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='bumple-downloader',
    version='0.1.1',
    packages=find_packages(),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    requires=["Django", ],
)