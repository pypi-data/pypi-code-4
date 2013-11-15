# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name = "dj-cli",
    version = "0.2",
    description = "A simple wrapper for django-admin.py, with virtualenv support.",
    author = u"Bahadır Kandemir",
    author_email = "kandemir@gmail.com",
    url = "https://github.com/bahadir/dj",
    packages = ['dj'],
    scripts=['bin/dj'],
    requires=['virtualenv', 'pip'],
) 
