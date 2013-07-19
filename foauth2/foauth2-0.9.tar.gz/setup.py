#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="foauth2",
      version="0.9",
      description="Library for OAuth version 2 'Bearer Token'",
      author="Jack Diederich",
      author_email="jackdied@gmail.com",
      url="http://github.com/jackdied/foauth2",
      packages = find_packages(),
      license = "MIT License",
      keywords="oauth",
      zip_safe = True,
      py_modules=['foauth2'],
      classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
     )
