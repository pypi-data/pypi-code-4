#!/usr/bin/env python
# Copyright 2013, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Josef Skladanka <jskladan@redhat.com>

from distutils.core import setup

setup(  name = 'resultsdb_api',
        py_modules = ['resultsdb_api'],
        version = '0.1.0',
        description = 'Library for simplifying the communication with ResultsDB',
        author = 'Josef Skladanka',
        author_email = 'jskladan@redhat.com',
        url = "https://bitbucket.org/rajcze/resultsdb",
        install_requires = ['requests'],
        classifiers = [
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Topic :: Internet",
            "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],

     )

