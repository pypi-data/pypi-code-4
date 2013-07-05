#!/usr/bin/env python
# encoding=UTF-8

from distutils.core import setup

setup(
    name = 'http1',
    version = '0.1.3',
    author = 'Michel Casabianca',
    author_email = 'michel.casabianca@gmail.com',
    packages = ['http1'],
    url = 'http://pypi.python.org/pypi/http1/',
    license = 'Apache Software License',
    description = 'HTTP1 is an API to perform HTTP requests in a single call.',
    long_description=open('README').read(),
)

