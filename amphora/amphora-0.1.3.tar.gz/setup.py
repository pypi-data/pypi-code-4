#!/usr/bin/env python
import sys
from setuptools import setup

install_requires = ["gevent", "amqp", "docutils>=0.7"]
if sys.version_info[:2] < (2, 7):
    install_requires += ['weakrefset']


setup(name='amphora',
      version='0.1.3',
      description='AMQP RPC for services based on gevent',
      author='Vladimir Lagunov',
      author_email='lagunov.vladimir@gmail.com',
      url='http://bitbucket.org/werehuman/amphora/',
      packages=['amphora'],
      license="BSD v3",
      keywords="AMQP, RPC, gevent",
      install_requires=install_requires,
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: POSIX",
          # "Operating System :: Microsoft :: Windows",  # not tested
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta"]
  )
