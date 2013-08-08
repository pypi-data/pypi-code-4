# -*- coding: utf-8 -*-
"""
    chard setup script

    blah blah blah

    :copyright: uniphil 2013
    :license: dwtfyw. and i like coffee.
"""

from sys import version_info
from setuptools import setup


with open('readme.md') as readme_file:
    readme = readme_file.read()

setup(
    name='chard',
    version='0',
    author='Phil Schleihauf',
    author_email='uniphil@gmail.com',
    url='https://github.com/uniphil/chard',
    license='blah blah blah',
    description='MongoDB Introspection-ish. ...',
    long_description=readme,
    install_requires=[] if version_info >= (2, 7, 0) else ['ordereddict'],
    py_modules=['chard'],
)
