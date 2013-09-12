#!/usr/bin/env python

from setuptools import setup

requires = ['requests',
		'jsonschema',
		'sqlahelper',
            'sqlalchemy_schemadisplay',
            'sqlalchemy',
            'pyramid_mailer']

setup(name='pyramid_rest_framework',
      version='0.0.4',
      description='Rest wrapper for pyramid web server',
      author='Stas Kaledin',
      author_email='staskaledin@gmail.com',
      url='https://bitbucket.org/sallyruthstruik/pyramid-rest-framework',
      packages=['pyramid_rest', 
            'pyramid_rest.security', 
            'pyramid_rest.files',
            'pyramid_rest.request_watcher'],
      install_requires = requires
     )
