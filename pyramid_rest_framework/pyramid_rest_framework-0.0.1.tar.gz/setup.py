#!/usr/bin/env python

from setuptools import setup

requires = ['requests',
			'jsonschema',
			'sqlahelper']

setup(name='pyramid_rest_framework',
      version='0.0.1',
      description='Rest wrapper for pyramid web server',
      author='Stas Kaledin',
      author_email='staskaledin@gmail.com',
      url='https://bitbucket.org/sallyruthstruik/pyramid-rest-framework',
      packages=['pyramid_rest', ],
      install_requires = requires
     )