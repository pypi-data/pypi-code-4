#!/usr/bin/env python

from setuptools import setup

setup(
        name='beatport',
        version='0.0.1',
        author='cburmeister',
        author_email='burmeister.corey@gmail.com',
        install_requires=[
            'requests',
            ],
        py_modules=[
            'beatport'
            ],
        )
