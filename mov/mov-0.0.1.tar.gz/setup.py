#!/usr/bin/env python
#coding=utf8

from setuptools import setup


setup(name='mov',
      version='0.0.1',
      author='Haukur Páll Hallvarðsson',
      author_email='hph@hph.is',
      url='https://github.com/hph/mov/tarball/0.0.1',
      license='MIT',
      py_modules = ['mov'],
      entry_points={'console_scripts': ['mov = mov:main']},
      extras_require={'docopt': 'docopt'})
