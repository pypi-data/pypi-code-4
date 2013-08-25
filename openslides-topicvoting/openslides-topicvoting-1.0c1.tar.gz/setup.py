#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for the Topic Voting Plugin for OpenSlides.
"""

from setuptools import setup, find_packages

# The following commented unique number is used for detecting this import.
from openslides_topicvoting import NAME, VERSION, DESCRIPTION  # Ohf9du1Kae8aiVayu3ahSaiZei0PhugiSu1eiMai


with open('README.rst') as readme:
    long_description = readme.read()


with open('requirements_production.txt') as requirements_production:
    install_requires = requirements_production.readlines()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author='Team of Topic Voting Plugin for OpenSlides, see AUTHORS',
    author_email='openslides-topicvoting@normanjaeckel.de',
    url='https://github.com/normanjaeckel/openslides-topicvoting',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2'],
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires)
