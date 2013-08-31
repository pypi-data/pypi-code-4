# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import dirname, join

setup(
    name='tordjango',
    version='0.1',
    author='Will Barton',
    author_email='willbarton@gmail.com',
    description='Simple management command to serve Django via Tornado',
    long_description=open('README.md').read(),
    url='http://github.com/gulielmus/tordjango',
    install_requires=["django", "tornado",],
    packages=find_packages(),
    license='BSD',
)

