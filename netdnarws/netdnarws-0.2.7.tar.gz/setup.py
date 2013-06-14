#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="netdnarws",
    version="0.2.7",
    description="A Python REST Client for NetDNA REST Web Services",
    author="NetDNA Developer Team",
    author_email = "devteam@netdna.com",
    license = "GPL v3",
    keywords = "NetDNA CDN API REST",
    packages=['netdnarws'],
    include_package_data=True,
    install_requires=[
      'requests',
      'requests_netdna',
      'requests_oauth',
      'certifi'
    ],
    url='http://developer.netdna.com',
)
