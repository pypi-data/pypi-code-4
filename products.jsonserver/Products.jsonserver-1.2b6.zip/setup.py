# -*- coding: utf-8 -*-
"""
This module contains the Zope2 product jsonserver: A JSON-RPC server for Zope2
"""
import os
from setuptools import setup, find_packages
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2b6'

long_description = (
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='Products.jsonserver',
      version=version,
      description="A JSON-RPC server for Zope2",
      long_description=long_description,
      classifiers=[
        'Framework :: Zope2',
        'Framework :: Plone',
        'Programming Language :: Python',
        ],
      keywords='json json-rpc',
      author='Tom Gross',
      author_email='itconsense@gmail.com',
      url='http://pypi.python.org/pypi/Products.jsonserver/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools', ],
      entry_points=""" """,
      )
