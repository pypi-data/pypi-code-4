#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "massresize",
    version = "1.2.0",
    url = 'https://github.com/sikaondrej/massresize/',
    license = 'MIT',
    description = "Mass image resize",
    author = 'Ondrej Sika',
    author_email = 'ondrej@ondrejsika.com',
    py_modules = ["libmassresize"],
    scripts = ["massresize", "massresize-gui"],
    include_package_data = True,
    zip_safe = False,
)
