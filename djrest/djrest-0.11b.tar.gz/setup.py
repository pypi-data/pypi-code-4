#!/usr/bin/env python
#
#The MIT License (MIT)
#
#djrest - api for creating simple rest service with django
#Copyright (C) 2013 Humberto Rojas <hrojasc(at)ieee.org>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

DESCRIPTION = "api for creating simple rest service with django"

LONG_DESCRIPTION = """djrest is a simple api for creating restfull
webservices with django using a flask like syntax."""

import sys

from distutils.core import setup
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name="djrest",
    version="0.11b",
    author="Humberto Rojas",
    author_email="hrojasc(at)ieee.org",
    url="http://github.com/humwerthuz/djrest",
    download_url="https://github.com/humwerthuz/djrest/archive/djrest-0.1b.zip",
    license="MIT",
    packages=[
        "djrest",
        "djrest.common",
        "djrest.http"
    ],
    py_modules=[
        "djrest.common.api",
        "djrest.common.helpers",
        "djrest.http.responses"
    ],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms="any",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
