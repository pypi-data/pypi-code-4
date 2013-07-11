#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('djaloha').__version__

setup(
    name='apidev-djaloha',
    version = VERSION,
    description='Django integration for aloha HTML5 editor',
    packages=['djaloha','djaloha.templatetags'],
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='BSD',
    long_description=open('README.rst').read(),
    url = "https://github.com/ljean/djaloha/",
    download_url = "https://github.com/ljean/djaloha/tarball/%s" % (VERSION),
    zip_safe=False,
    install_requires = ['django-floppyforms==0.4.7',]
)
