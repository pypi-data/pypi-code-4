#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pearpass',
    version='1.0.2',
    description="Scripts for managing secrets with Octopus and GnuPG.",
    author="Miles Shang",
    author_email='mail@mshang.ca',
    url='https://github.com/mshang/pearpass',
    scripts=['pearpass'],
    license='LICENSE.txt',
    install_requires=['requests'],
)
