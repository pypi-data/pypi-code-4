# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '1.3'

tests_require = [
    'infrae.wsgi [test]',
    ]


setup(name='infrae.rest',
      version=version,
      description="Define a REST API to access and manage Zope 2 content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva cms rest api zope',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['infrae',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'grokcore.view',
        'martian',
        'setuptools',
        'zeam.component',
        'zope.browser',
        'zope.component',
        'zope.event',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
