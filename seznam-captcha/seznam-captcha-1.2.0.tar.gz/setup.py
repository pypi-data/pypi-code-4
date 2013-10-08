#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "seznam-captcha",
    version = "1.2.0",
    url = 'https://github.com/sikaondrej/seznam-captcha/',
    download_url = 'https://github.com/sikaondrej/seznam-captcha/',
    license = 'MIT Licence',
    author = "Ondrej Sika",
    aurhor_email = "ondrej@ondrejsika.com",
    description = "Wraper for Seznam Captcha",
    py_modules = ["seznam_captcha", ],
    install_requires = ["requests"],
    include_package_data = True,
    zip_safe = False,
)
