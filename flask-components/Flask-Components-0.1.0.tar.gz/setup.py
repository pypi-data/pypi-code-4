#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from imp import load_source


setup(
    name='Flask-Components',
    version=load_source('', 'src/flask_components/_version.py').__version__,
    description='A simple flask extension to discover files in a declared '
                'array of components.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/flask-components',
    package_dir={'flask_components': 'src/flask_components'},
    packages=find_packages('src'),
    install_requires=[
        'Flask >= 0.9.0',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
        ]
    }
)
