#!/usr/bin/env python

PROJECT = 'filespy'
VERSION = '1.1'

from setuptools import (
    setup,
    find_packages,
)

setup(
    name=PROJECT,
    version=VERSION,

    description='find changes in a directory',

    author='Boris Kaul',
    author_email='me@boriskaul.com',

    url='https://github.com/localvoid/py-filespy/',
    download_url='https://github.com/localvoid/py-filespy/tarball/master',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
    ],

    platforms=['Any'],

    scripts=[],
    provides=[],
    install_requires=[],

    packages=find_packages(),
    zip_safe=True,
)
