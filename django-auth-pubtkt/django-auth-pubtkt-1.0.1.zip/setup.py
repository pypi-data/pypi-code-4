#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-auth-pubtkt",
    version = "1.0.1",
    author = "Alexander Vyushkov",
    author_email = "alex.vyushkov@gmail.com",
    description = "Implementation of mod_auth_pubtkt as Django middleware",
    license = "BSD",
    keywords = "django auth mod_auth_pubtkt",
    url = "https://github.com/Baguage/django-auth-pubtkt",
    packages=['django_auth_pubtkt', 'tests'],
    long_description=read('README'),
    install_requires=[" M2Crypto", "Django >= 1.3",],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
    ],
)