#!/usr/bin/env python

import os
import sys

VERSION = '0.2.1'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'contour',
]

requires = []

try:
    license = open('LICENSE').read(),
except:
    licens = 'APACHE 2.0'

setup(
    name='contour',
    version=VERSION,
    description='Python configuration.',
    author='Beau Lyddon',
    author_email='lyddonb@gamil.com',
    url='http://github.com/lyddonb/contour',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE'], 'contour': ['*.pem']},
    package_dir={'contour': 'contour'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
