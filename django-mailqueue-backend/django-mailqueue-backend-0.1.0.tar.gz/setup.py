from os import path as os_path
from setuptools import setup, find_packages

import mailqueue_backend

description = long_description = "Simple Mail Queuing Backend for Django"
if os_path.exists('README.rst'):
    long_description = open('README.rst').read()

version = mailqueue_backend.VERSION

def read(fname):
    return open(os_path.join(os_path.dirname(__file__), fname)).read()

setup(name='django-mailqueue-backend',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Communications :: Email",
          "Topic :: Utilities",
          "Framework :: Django",
          ],
      keywords='django mail queue smtp backend',
      maintainer='Dwaiter.com',
      maintainer_email='dev@dwaiter.com',
      url='https://bitbucket.org/dwaiter/django-mailqueue-backend',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['django>=1.2','queues>=0.6.2']
    )