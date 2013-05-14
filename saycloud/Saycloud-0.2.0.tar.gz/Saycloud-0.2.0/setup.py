#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import join, dirname

def read(fname):
    return open(join(dirname(__file__), fname)).read()

PKG = 'Saycloud'
VERSION = '0.2.0'

requires = ['setuptools', 'soundcloud']
scripts = ['bin/saycloud']

setup(
    name=PKG,
    version=VERSION,
    description="Saycloud - text to Soundcloud",
    long_description=read('README.rst'),
    author="Ross Duggan",
    author_email="ross.duggan@acm.org",
    url="http://github.com/duggan/saycloud",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    scripts=scripts,
    license="MIT License",
    keywords="soundcloud, saycloud",
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ]
)
