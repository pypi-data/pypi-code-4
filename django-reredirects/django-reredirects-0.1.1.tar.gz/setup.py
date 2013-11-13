#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.md').read()

setup(
    name='django-reredirects',
    version=__import__('reredirects').__version__,
    description='Django Redirects, but with regex and without the sites framework.',
    long_description=readme + '\n\n' + history,
    author='John-Michael Oswalt',
    author_email='jmoswalt@gmail.com',
    url='https://github.com/jmoswalt/django-reredirects',
    packages=[
        'reredirects',
    ],
    package_dir={'django-reredirects': 'reredirects'},
    include_package_data=True,
    install_requires=[
        'django>=1.4',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-reredirects',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)