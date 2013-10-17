# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from Cython.Build import cythonize

if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__

setup(
    name='python-kyototycoon-binary',
    version='0.0.1',
    description='A lightweight KyotoTycoon client library',
    long_description=open('README.rst').read(),
    author='Studio Ousia',
    author_email='admin@ousia.jp',
    url='http://github.com/studio-ousia/python-kyototycoon-binary',
    packages=find_packages(),
    license=open('LICENSE').read(),
    ext_modules=cythonize('bkyototycoon/client.pyx'),
    include_package_data=True,
    keywords=[],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=[
        'gsocketpool',
        'msgpack-python',
    ],
    tests_require=[
        'nose',
        'mock',
        'setuptools_cython',
    ],
    test_suite = 'nose.collector'
)
