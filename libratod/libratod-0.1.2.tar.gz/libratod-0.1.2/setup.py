#!/usr/bin/env python

# Copyright (c) 2013 Aaron Fay / Strathcom Media http://strathcom.com/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


from setuptools import setup

required = [
    'librato-metrics',
    'psutil',
]

setup(
    name="libratod",
    version='0.1.2',
    description="Simple daemon to send stats to librato metrics.",
    long_description="Collects system information using psutil and posts that to your Librato Metrics account at a set interval. Useful for health-check/system monitoring.",
    scripts=['libratod'],
    author="Aaron Fay",
    author_email="aaron.j.fay@gmail.com",
    url = "https://github.com/Strathcom/librato-daemon",
    packages = [],
    install_requires=required,
    license = 'MIT',
    platforms = 'Posix; MacOS X; Windows',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Monitoring',
    ],
)
