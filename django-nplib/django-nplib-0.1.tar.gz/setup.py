# -*- coding: utf-8 -*-
#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'django-nplib',
    version = '0.1',
    description = 'Hopefully useful django decorators, middleware and misc utility functions',
    author = 'Nick Pack',
    author_email = 'nick@nickpack.com',
    url = 'https://github.com/nickpack/django-nplib',
    packages = [
        'nplib',
        'nplib.decorators',
        'nplib.middleware'
    ],
)