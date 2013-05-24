#!/usr/bin/env python

from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(name='Flipkart',
      version='1.0',
      packages=['fk'],
      description='Flipkart python book search API',
      author='Vengadanathan Srinivasan',
      license = "BSD",
      author_email='fantastic.next@gmail.com',
      url='https://code.google.com/p/flipkart-books-python-api/wiki/README',
      keywords = "Flipkart python book search API" ,
      install_requires=['beautifulsoup4'],
      long_description=read('README.txt'),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS"
        ],
      
     )