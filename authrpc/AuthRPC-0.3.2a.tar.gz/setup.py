#!/usr/bin/env python
from distutils.core import setup
try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: OS Independent',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Internet :: WWW/HTTP :: WSGI']

setup(name             = 'AuthRPC',
      version          = '0.3.2a',
      packages         = ['AuthRPC', 'AuthRPC.server', 'AuthRPC.client'],
      install_requires = 'WebOb>=1.2.3',
      author           = 'Ben Croston',
      author_email     = 'ben@croston.org',
      description      = 'A JSONRPC-like client and server with additions to enable authenticated requests',
      long_description = open('README.txt').read() + open('CHANGELOG.txt').read(),
      license          = 'MIT',
      keywords         = 'json, rpc, wsgi, auth',
      url              = 'http://www.wyre-it.co.uk/authrpc/',
      classifiers      = classifiers,
      platforms        = ['Any'],
      cmdclass         = {'build_py': build_py})
