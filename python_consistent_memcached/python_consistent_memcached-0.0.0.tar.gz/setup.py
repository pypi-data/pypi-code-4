#!/usr/bin/env python
"""
memcached_rehasher
======

A pure python implementation of a consistent hasher for memcached.
Its missrate is similar to continuum, but it has O(1) per request
performane vs continiums O(lg(n)) per request performnace where n is
the number of servers in your memcached collecion.

"""

from setuptools import setup

setup(
    name='python_consistent_memcached',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='python-memcached with consistent hashing',
    long_description=__doc__,
    py_modules = [
        "consistent_memcached/__init__",
        ],
    packages = ["consistent_memcached"],
    zip_safe=True,
    license='GPL',
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        ],
    url = "https://github.com/wnyc/python_consistent_memcached",
    install_requires = [
        'python_memcached',
        ]
)

