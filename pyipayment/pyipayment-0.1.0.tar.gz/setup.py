#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='pyipayment',
    version='0.1.0',
    description='Python iPayment API',
    author='Jeff Tchang',
    author_email='jeff.tchang@gmail.com',
    url='http://github.com/tachang/pyipayment/',
    zip_safe = False,
    long_description="Python iPayment API",
    packages=[
        'pyipayment',
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
