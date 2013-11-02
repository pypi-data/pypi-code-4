#!/usr/bin/env python

from distutils.core import setup

setup(name = "django-moreforms",
      version = "1.0",
      description = "Contains helpful fields for Django, such as a FieldTree (" +
        "a simple way to get a field chain) and date-related fields.",
      author = "Jordan Nath",
      author_email = "jordannh@sent.com",
      
      packages = ['moreforms',
                  'moreforms.date',
                  'moreforms.fancy',
                  'moreforms.fieldtree',
                  'moreforms.templatetags',]
    )