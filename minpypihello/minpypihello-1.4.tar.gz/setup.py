#!/usr/bin/env python

from distutils.core import setup

setup(name='minpypihello',
      version='1.4',
      description='Minimal PyPI Package Example',
      author='Pili Hu',
      author_email='me@hupili.net',
      url='https://github.com/hupili/min-pypi-hello',
      license="MIT",
      packages=['minpypihello'],
      scripts=['myhello']
     )
