#!/usr/bin/env python

import os
import sys

import greencard

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
    name='greencard',
    version=greencard.__version__,
    description='Cookiecutter template for a Python package.',
    long_description=readme + '\n\n' + history,
    author='Taylor "Nekroze" Lawson',
    author_email='nekroze@eturnilnetwork.com',
    url='https://github.com/Nekroze/greencard',
    packages=[
        'greencard',
    ],
    entry_points={
        'console_scripts': [
            'greencard = greencard.greencard:main',
            ]
    },
    package_dir={'greencard': 'greencard'},
    include_package_data=True,
    install_requires=[
        'librarian>=0.2.6',
    ],
    license="MIT",
    zip_safe=False,
    keywords='greencard',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
