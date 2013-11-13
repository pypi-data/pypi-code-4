#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.0.1'
LONG_DESC = """\
A python wrapper to the USPS api, currently only supports address validation
"""

setup(name='python-usps2',
      version=VERSION,
      description="A python wrapper to the USPS api, currently only supports address validation",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='usps api shipping',
      author='Derek Stegelman',
      author_email='email@stegelman.com',
      maintainer = 'Derek Stegelman',
      maintainer_email = 'email@stegelman.com',
      url='http://github.com/dstegelman/python-usps',
      license='New BSD License',
      packages=find_packages(exclude=['usps']),
      zip_safe=False,
      install_requires=[
      ],

      )
