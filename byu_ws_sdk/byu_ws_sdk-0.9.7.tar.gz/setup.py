#!/usr/bin/env python2.7

from setuptools import setup, find_packages
import sys

if sys.version_info < (2, 7, 0) or sys.version_info >= (3, 0, 0):
    sys.stderr.write("byu_ws_sdk currently requires Python 2.7.\n")
    sys.exit(-1)

# pypi requires reStructuredText and github requires Markdown, so we convert like so
# requires http://johnmacfarlane.net/pandoc/
# pandoc --from=markdown --to=rst --output=README.rst README.md

with open('README.rst') as rm_file:
    long_description = rm_file.read()

setup(name='byu_ws_sdk',
      version='0.9.7',
      description='A Python SDK for calling BYU REST web services.',
      long_description=long_description,
      author='BYU OIT Core Application Engineering',
      author_email='paul_eden@byu.edu',
      url='https://github.com/byu-oit-core-appeng/byu-ws-sdk-python',
      packages=find_packages(),
      data_files=[('', ['README.md', 'README.rst', 'LICENSE'])],
      test_suite="byu_ws_sdk.test",
      license="MIT",
      requires=['requests (>=0.14.1, <=0.14.2)', 'simplejson', 'decorator']
      )
