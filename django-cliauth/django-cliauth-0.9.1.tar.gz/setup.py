#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Sergio Campos on 2012-01-10.
"""

from setuptools import setup

setup(name='django-cliauth',
      version='0.9.1',
      author='Sergio Oliveira',
      author_email='seocam@seocam.com',
      license='GPL2',
      description='Authenticate Apache2 (basic auth) using your Django DB', 
      url='https://bitbucket.org/seocam/django-cliauth',
      packages=(
          'cliauth',
          'cliauth.management',
          'cliauth.management.commands',
      ),
      install_requires=(
        'django>=1.2', 
    )
)
