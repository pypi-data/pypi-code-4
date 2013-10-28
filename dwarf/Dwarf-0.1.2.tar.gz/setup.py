#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

# required is a list of requirements
# e.g. ["Flask==0.10.1","Jinja2==2.7.1","Markdown==2.3.1","MarkupSafe==0.18"]
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='Dwarf',
    version='0.1.2',
    author='Joeri Poesen',
    author_email='joeri@bantalabs.com',
    packages=['dwarf'],
    url='http://pypi.python.org/pypi/dwarf/',
    license='LICENSE',
    description='yet another static site generator',
    long_description=open('README.txt').read(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],


)
