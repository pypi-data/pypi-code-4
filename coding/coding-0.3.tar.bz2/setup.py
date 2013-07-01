#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2010, 2013 K Richard Pixley.
#
# See LICENSE for details.
#
# Time-stamp: <30-Jun-2013 17:28:51 PDT by rich@noir.com>

import os
import platform

import distribute_setup
distribute_setup.use_setuptools()

import setuptools
import coding

me='K Richard Pixley'
memail='rich@noir.com'

setup_requirements = [
    	'nose',
        'setuptools_hg',
        ]

version_tuple = platform.python_version_tuple()
version = platform.python_version()

if version not in [
    '3.0.1',
    '3.1.5',
    '3.3.1',
    ]:
    setup_requirements.append('setuptools_lint')

if version not in [
    '3.0.1',
    ]:
    setup_requirements.append('sphinx>=1.0.5')


setuptools.setup(
    name='coding',
    version='0.3',
    author=me,
    maintainer=me,
    author_email=memail,
    maintainer_email=memail,
    keywords='enum coding',
    url='http://bitbucket.org/krp/coding',
    download_url='https://bitbucket.org/krp/coding/get/default.tar.bz2',
    description='An answer to the question of python enums.',
    license='MIT',
    long_description=coding.__doc__,
    setup_requires=setup_requirements,
    install_requires=[
        ],
    py_modules=['coding'],
    include_package_data=True,
    test_suite='nose.collector',
    scripts = [
        ],
    requires=[
        ],
    provides=[
        'coding',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
