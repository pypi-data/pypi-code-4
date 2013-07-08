#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup

reload(sys).setdefaultencoding("UTF-8")

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    LONG_DESCRIPTION = readme.read().decode('utf8')

setup(
    name='pyvkoauth',
    version='0.9',
    author='Azat Kurbanov',
    author_email='cordalace@gmail.com',
    description='OAuth authentification for vk.com',
    long_description=LONG_DESCRIPTION,
    license='Apache License 2.0',
    url='https://bitbucket.org/cordalace/pyvkoauth',
    install_requires=['lxml>=2.3.3'],
    keywords='vkontakte vk oauth auth browserless',
    py_modules=['pyvkoauth'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ],
)

