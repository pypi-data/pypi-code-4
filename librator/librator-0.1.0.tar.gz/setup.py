#!/usr/bin/env python

import os
import sys

import librator

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
    name='librator',
    version=librator.__version__,
    description='A method of automatically constructing a Librarian library database from a directory of yaml files or the reverse.',
    long_description=readme + '\n\n' + history,
    author='Taylor "Nekroze" Lawson',
    author_email='nekroze@eturnilnetwork.com',
    url='https://github.com/Nekroze/librator',
    packages=[
        'librator',
    ],
    entry_points={
        'console_scripts': [
            'librator = librator.librator:main',
            'libratorcard = librator.librator:cardmain',
            ]
    },
    package_dir={'librator': 'librator'},
    include_package_data=True,
    install_requires=[
        'pyyaml>=3.10',
        'librarian>=0.2.3',
    ],
    license="MIT",
    zip_safe=False,
    keywords='librator',
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
    tests_require=[
        'nose>=1.3.0',
    ],
    test_suite='nose.collector',
)
