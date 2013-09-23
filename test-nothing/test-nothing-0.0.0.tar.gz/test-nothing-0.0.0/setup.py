#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
from setuptools import setup

from distutils.core import setup

setup(name='test-nothing',
      version='0.0.0',
      description='Just an empty project to test pypi registering',
      author='Pierre-Francois Carpentier',
      author_email='carpentier.pf [ at ] gmail.com',
      license='WTFPL',
      url='',
      packages = ['test_nothing',],
      package_dir = {'': 'src'},
     )
