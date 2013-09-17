#!/usr/bin/env python
from setuptools import setup

setup(name="blobuploader",
      version="0.8",
      author="Mihai Tabara",
      author_email="mtabara@mozilla.com",
      url='https://github.com/catlee/blobber',
      scripts = ["blobberc.py"],
      install_requires=["poster", "requests", "docopt"],
      description='Specific client for uploading blob files on Mozilla server',
      )
