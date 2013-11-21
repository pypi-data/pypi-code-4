#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

packages = [
    'pelican_delicious',
]

requires = [
    'requests',
    'beautifulsoup4'
]

setup(
    name='pelican-delicious',
    version='0.0.1',
    description='Easily embed delicious bookmarks in your Pelican articles.',
    long_description=readme,
    author='Yohann Lepage',
    author_email='yohann@lepage.info',
    url='https://github.com/2xyo/pelican-delicious',
    packages=packages,
    package_data={'': ['LICENSE', ]},
    package_dir={'pelican_delicious': 'pelican_delicious'},
    include_package_data=True,
    install_requires=requires,
    setup_requires=['nose>=1.0'],
    license='BSD',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: BEER-WARE',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
    ),
)
