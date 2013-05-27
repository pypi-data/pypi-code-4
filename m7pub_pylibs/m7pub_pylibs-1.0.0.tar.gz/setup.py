#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup (
    name                = 'm7pub_pylibs',
    version             = '1.0.0',
    author              = 'Iqbal Abdullah',
    author_email        = 'iqbal@marimore.co.jp',
    # List out where your code lives, with __init__.py
    packages            = [
        'm7pub_pylibs', 
        'm7pub_pylibs.dev', 
        'm7pub_pylibs.jp', 
        'm7pub_pylibs.utils', 
    ],
    #package_data        = {'m7pvt_pylibs': ['django/templates/*.html']},
    scripts             = [],   # if we have any scripts in bin
    url                 = '',
    license             = 'LICENSE.txt',
    description         = "m7pub_pylibs are libraries used by MARIMORE and are opened sourced",
    long_description    = open('README.rst').read(),
    install_requires    = [
        #"Django >= 1.4",
    ],
)
