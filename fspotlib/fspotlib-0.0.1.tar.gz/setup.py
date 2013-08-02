#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
import fspotlib

setup(
    name='fspotlib',
    version=fspotlib.__version__,
    packages=find_packages(),
    author="fspot",
    author_email="fred@fspot.org",
    description="test publishing on pypi",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='http://github.com/fspot/fspotlib',
    entry_points = {
        'console_scripts': [
            'fspot-say = fspotlib.core:say_hello',
        ],
    },
    license='WTFPL',
)

