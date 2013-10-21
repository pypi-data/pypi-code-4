#!/usr/bin/env python
# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages


setup(
    name="zdup",
    version="1.2",

    description="Z Duplicity",
    license="Apache License v2.0",
    url="https://github.com/dstufft/zdup",

    author="Donald Stufft",
    author_email="donald@stufft.io",

    classifiers=[
        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    py_modules=["zdup"],

    install_requires=[
    ],

    entry_points={
        "console_scripts": [
            "zdup = zdup:main",
        ],
    },

    zip_safe=False,
)
