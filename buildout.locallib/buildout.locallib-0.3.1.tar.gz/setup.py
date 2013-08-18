# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.3.1'
long_description = open("README.txt").read()

classifiers = [
   "Development Status :: 4 - Beta",
   "Intended Audience :: Developers",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development :: Build Tools",
   "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='buildout.locallib',
    version=version,
    description='buildout.locallib use egg-packages installed on site-packages folder.',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['zc.buildout'],
    author='Takayuki SHIMIZUKAWA',
    author_email='shimizukawa at gmail.com',
    url='http://bitbucket.org/shimizukawa/buildout.locallib/',
    license='PSL',
    namespace_packages=['buildout'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=True,
    entry_points="""
       [zc.buildout.extension]
       ext = buildout.locallib:load
    """,
)

