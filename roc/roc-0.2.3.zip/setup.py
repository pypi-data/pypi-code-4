#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()

setup(
    # Bla-bla-bla
    name='roc',
    description='XMLRPC with classes',
    long_description=readme,
    author='Peter Demin',
    author_email='poslano@gmail.com',
    url='https://github.com/peterdemin/python-roc',
    license="BSD",
    zip_safe=False,
    keywords='roc xml rpc fitnesse slim vagrant',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],

    # What actually matters
    version='0.2.3',
    packages=['roc'],
    package_dir={'roc': 'roc'},
    include_package_data=True,
)
