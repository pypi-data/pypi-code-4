#!/usr/bin/env python
#coding=utf-8

import corrector
from distutils.core import setup

setup(name='corrector',
      version=corrector.__version__,
      description='A spelling corrector.',
      long_description=open('README.md').read(),
      author='solos',
      author_email='solos@solos.so',
      py_modules=['corrector'],
      scripts=['corrector.py'],
      license='MIT',
      platforms=['any'],
      url='https://github.com/solos/corrector')
