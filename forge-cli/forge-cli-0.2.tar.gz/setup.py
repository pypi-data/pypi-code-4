#!/usr/bin/python

import os
import sys

import forge

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

if sys.version_info <= (2 , 6):
    REQUIRES = ['argparse',]
else:
    REQUIRES = []

setup(
    name='forge-cli',
    version=forge.__version__,
    description='forge is a command line tool that allows to execute modules to configure a linux system',
    long_description=readme + '\n\n' + history,
    author='Luis Morales',
    author_email='luismmorales@gmail.com',
    url='https://github.com/lacion/forge',
    entry_points = { "console_scripts": [ "forge = forge.forge:run", ] },
    packages=[
        'forge',
    ],
    package_dir={'forge': 'forge'},
    include_package_data=True,
    install_requires=REQUIRES,
    license="BSD",
    zip_safe=False,
    keywords='forge',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
