#!/usr/bin/env python
"""Distutils installer for rabbitfixture."""

from setuptools import setup, find_packages


setup(
    name='rabbitfixture',
    version="0.3.4",
    packages=find_packages('.'),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    description='Magic.',
    install_requires=[
        'amqplib >= 0.6.1',
        'fixtures >= 0.3.6',
        'setuptools',
        'testtools >= 0.9.12',
        ])
