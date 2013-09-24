#!/usr/bin/env python

from distutils.core import setup

setup(name='pyzmq-wrapper',
      version='0.1.1b',
      description='Wrapper classes for pyzmq',
      long_description='Please visit https://github.com/supercoderz/pyzmq-wrapper for more details',
      author='Narahari Allamraju',
      author_email='anarahari@gmail.com',
      url='https://github.com/supercoderz/pyzmq-wrapper',
      packages=['zmqwrapper'],
      requires=['pyzmq','pytest'],
     )
