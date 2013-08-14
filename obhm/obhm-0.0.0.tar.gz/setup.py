#!/usr/bin/env python
"""
obhm
======

One Banana Host Monitor

Stupid simple host monitoring for people other things to think about. 

"""

from setuptools import setup


setup(
    name='obhm',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='One Banana Host Monitoring for people with other things to think about',
    long_description=__doc__,
    py_modules = [
        "obhm/__init__",
        "obhm/server",
        "obhm/load",
        ],
    packages = ["obhm"],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        "scripts/obhm",
        ],
    url = "https://github.com/ob/obhm",
    install_requires = [
        'python-gflags',
        ]
)

