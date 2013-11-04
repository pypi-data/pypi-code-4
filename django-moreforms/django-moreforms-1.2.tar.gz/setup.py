#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(name = "django-moreforms",
      version = "1.2",
      description = "Contains helpful fields for Django, such as a FieldTree (" +
        "a simple way to get a field chain) and date-related fields.",
      author = "Jordan Nath",
      author_email = "jordannh@sent.com",
      
      packages = find_packages(where='.'),
      
      include_package_data=True,
      
      package_data = {
          'moreforms' : ['static/*'],
      }
)