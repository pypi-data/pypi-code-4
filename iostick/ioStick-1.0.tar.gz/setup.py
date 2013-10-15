#!/usr/bin/env python

from setuptools import setup

setup(name='ioStick',
      version='1.0',
      description='Python wrapper for webLinux IoStick',
      author='Tom Carter',
      author_email='admin@wlinux.mobi',
      url='http://wlinux.mobi/products/ioStick',
      packages=['ioStick'],
      install_requires='pySerial'
    )
