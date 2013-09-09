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

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='flask-cbv',
    version='0.0.1',
    description='Class based views for Flask.',
    long_description=readme + '\n\n' + history,
    author='Jindřich Smitka',
    author_email='smitka.j@gmail.com',
    url='https://bitbucket.org/jsmitka/flask-cbv',
    packages=[
        'flask_cbv',
        'flask_cbv.views',
    ],
    package_dir={'flask-cbv': 'flask_cbv'},
    include_package_data=True,
    install_requires=[
        'Flask>=0.10.1',
    ],
    license="BSD",
    zip_safe=False,
    keywords='flask-cbv',
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
    test_suite='tests',
)
