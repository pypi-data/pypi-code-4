#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='fspotlib',
    version="0.0.2",  # update it in __init__.py also. Now!
    install_requires=["clize"],
    packages=find_packages(),
    author="fspot",
    author_email="fred@fspot.org",
    description="test publishing on pypi",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='http://github.com/fspot/fspotlib',
    entry_points = {
        'console_scripts': [
            'fspot-say = fspotlib.core:main',
        ],
    },
    license='WTFPL',
)

