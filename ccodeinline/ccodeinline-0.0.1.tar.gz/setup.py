#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- file: setup.py -*-

from setuptools import setup, find_packages
import sys, os
import ccodeinline

version = ccodeinline.__version__ 

def readme():
    try:
        f = open('README.rst')
        return f.read()
    finally:
        f.close()

setup(name='ccodeinline',
      version=version,
      description="C/C++ code generation into a more enhanced environement.",
      long_description="""\
CCodeInline is also a property-model based Idiom. All Idiom are focused on certains part of the Communication Layer from File-Management to File-componnent and extension like Header and linking format to produce Compiled code working on module distutils.core.""",
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='ccodeinline',
      author='Maxiste Deas, Patrick Riendeau',
      author_email='maxistedeams@gmail.com',
      url='https://github.com/priendeau/Technical-PorteFolio/tree/master/Python/CCodeInline',
      license='OpenBSD',
      packages=find_packages(exclude=[]),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'numpy >= 1.7.1',
          'multiprocessing >= 0.70a1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
