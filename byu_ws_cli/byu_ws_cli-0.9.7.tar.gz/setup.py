#!/usr/bin/env python2.7

import sys

from setuptools import setup, find_packages


if sys.version_info < (2, 7, 0) or sys.version_info >= (3,):
    sys.stderr.write("byu_ws_cli currently requires Python 2.7.\n")
    sys.exit(-1)

# we only use the subset of markdown that is also valid reStructuredText so
# that our README.md works on both github (markdown) and pypi (reStructuredText)
with open("README.md") as rm_file:
    long_description = rm_file.read()

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='byu_ws_cli',
      version='0.9.7',
      description='A command-line web service client for calling BYU REST web services.',
      long_description=long_description,
      author='BYU OIT Core Application Engineering',
      author_email='paul_eden@byu.edu',
      url='https://github.com/byu-oit-core-appeng/byu-ws-cli-python',
      packages=find_packages(),
      data_files=[('', ['README.md', 'LICENSE'])],
      test_suite="byu_ws_cli.test",
      license="MIT",
      obsoletes=['oit_web_service_client'],
      install_requires=['byu_ws_sdk < 1.1.0'],
      scripts=['bin/call_byu_ws'],
      zip_safe=True,
      **extra
      )
