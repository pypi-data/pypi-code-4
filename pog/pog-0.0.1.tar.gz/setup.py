#!/usr/bin/env python

"""Pog: a command line Azkaban client."""

from setuptools import setup

setup(
    name='pog',
    version='0.0.1',
    description='Azkaban CLI',
    long_description=open('README.rst').read(),
    author='Matthieu Monsch',
    author_email='monsch@alum.mit.edu',
    url='http://github.com/mtth/pog/',
    license='MIT',
    py_modules=['pog'],
    classifiers=[
      'Development Status :: 2 - Pre-Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
    ],
    # install_requires=[],
    # entry_points={'console_scripts': []},
)
