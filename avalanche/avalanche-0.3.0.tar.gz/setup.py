#! /usr/bin/env python

#from distutils.core import setup
# use setuptools to upload docs
from setuptools import setup

setup(name = 'avalanche',
      description = 'Web Framework with a focus on testability and reusability',
      version = '0.3.0',
      license = 'MIT',
      author = 'Eduardo Naufel Schettino',
      author_email = 'schettino72@gmail.com',
      url = 'http://packages.python.org/avalanche/overview.html',
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      packages = ['avalanche'],
      install_requires = ['webob', 'jinja2'],
      long_description = open('doc/overview.rst').read(),
      )
