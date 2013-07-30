#!/usr/bin/env python2.7

import os
import sys
import subprocess

from setuptools import setup, find_packages


if sys.version_info < (2, 7, 0) or sys.version_info >= (3,):
    sys.stderr.write("byu_ws_sdk currently requires Python 2.7.\n")
    sys.exit(-1)

# pypi requires reStructuredText and github requires Markdown, so we convert like so
# requires http://johnmacfarlane.net/pandoc/
try:
    subprocess.check_call("pandoc --from=markdown --to=rst --output=README.rst README.md", shell=True)
    print("running pandoc to create README.rst from README.md")
except OSError:
    pass

readmeFile = 'README.rst'
if not os.path.exists(readmeFile):
    readmeFile = 'README.md'
with open(readmeFile) as rm_file:
    long_description = rm_file.read()

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='byu_ws_sdk',
      version='0.9.9',
      description='A Python SDK for calling BYU REST web services.',
      long_description=long_description,
      author='BYU OIT Core Application Engineering',
      author_email='paul_eden@byu.edu',
      url='https://github.com/byu-oit-core-appeng/byu-ws-sdk-python',
      packages=find_packages(),
      data_files=[('', ['README.md', 'README.rst', 'LICENSE'])],
      test_suite="byu_ws_sdk.test",
      license="MIT",
      requires=['requests (>=0.14.1, <=0.14.2)', 'simplejson', 'decorator'],
      zip_safe=True,
      **extra
      )
