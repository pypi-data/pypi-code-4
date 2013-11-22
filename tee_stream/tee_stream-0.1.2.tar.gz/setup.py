#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

from tee_stream import __version__

setup(
    name='tee_stream',
    version=__version__,
    author='Patrick Ng',
    author_email='pn.appdev@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/pnpnpn/tee-stream',
    license='MIT',
    description='',
    long_description=open('README.rst').read() if exists("README.rst") else "",
    install_requires=[
        
    ],
)
