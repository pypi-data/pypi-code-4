#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='pyboxapi',
    version='0.1.4',
    description='Python Box.com API',
    author='Jeff Tchang',
    author_email='jeff.tchang@gmail.com',
    url='http://github.com/tachang/pyboxapi/',
    zip_safe = False,
    long_description="Python Box.com API",
    packages=[
        'pyboxapi',
    ],
    requires=[
    ],
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
