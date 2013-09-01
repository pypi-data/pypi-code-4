#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "massresize",
    version = "1.0.0",
    url = 'http://ondrejsika.com/docs/massresize/',
    download_url = 'https://github.com/sikaondrej/massresize/',
    license = 'GNU LGPL v.3',
    description = "",
    author = 'Ondrej Sika',
    author_email = 'ondrej@ondrejsika.com',
    py_modules = ["libmassresize"],
    scripts = ["massresize", "massresize-gui"],
    include_package_data = True,
    zip_safe = False,
)
