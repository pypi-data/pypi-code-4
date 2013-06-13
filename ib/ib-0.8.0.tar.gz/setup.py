#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
readme = open('README.txt').read()
setup(name='ib',
      version='0.8.0',
      revision='r349',
      author='Colin.Alexander',
      author_email='colin.1.alexander@gmail.com',
      license='MIT',
      description='bPy is a third-party implementation of the API used for accessing the Interactive Brokers on-line trading system. IbPy implements functionality that the Python programmer can use to connect to IB, request stock ticker data, submit orders for stocks and futures, and more.',
      long_description=readme,
      packages=find_packages())

