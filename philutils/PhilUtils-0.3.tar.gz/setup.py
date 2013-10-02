#!/usr/bin/env python

# Name: setup.py
# Author: Philip Zerull
# Date Created: Thursday March 1, 2012
# Copyright 2012, Philip Zerull

import sys
from setuptools import setup, find_packages

setup(
    name='PhilUtils',
    use_hg_version=True,
    description="Phil Zerull's tiny library of miscellaneous functions",
    long_description="""
            This library contains a bunch of small miscellaneous functions,
            I've built over time but didn't seem to fit in their own package.

            For the foreseeable future, this library will undergo too many
            changes for me to suggest that anyone use this library and I plan
            on regularly shuffle things out of this library when I feel that
            they would be better organized in their own package.

            Use at your own risk.
        """,
    author='Philip Zerull',
    author_email='przerull@gmail.com',
    maintainer='Philip Zerull',
    maintainer_email='przerull@gmail.com',
    url='https://bitbucket.org/przerull/philutils',
        download_url='',
        packages=find_packages(),
        py_modules=[],
        scripts=[],
        ext_modules=[],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities'
        ],
    options=dict(),
    license='GNU Lesser General Public License',
    keywords=[],
    platforms=[],
    cmdclass=dict(),
    data_files=[],
    package_dir=dict(),
    setup_requires=['hgtools'],
    requires=[]
)
