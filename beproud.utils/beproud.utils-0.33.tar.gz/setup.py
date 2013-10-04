#!/usr/bin/env python

from setuptools import setup, find_packages
 
setup (
    name='beproud.utils',
    version='0.33',
    description='Dependency free utilities',
    author='Ian Lewis',
    author_email='ianmlewis@beproud.jp',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    namespace_packages=['beproud'],
    test_suite="beproud.utils.tests",
    zip_safe=True,
)
