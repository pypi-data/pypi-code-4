#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="slikio-python",
      version="0.0.1",
      description="Python library for SlikIO - Charts as a service",
      license="MIT",
      install_requires=["requests"],
      author="Daniel Brodsky, SlikIO",
      author_email="daniel@slik.io",
      url="http://github.com/SlikIO/slikio-python",
      packages = find_packages(),
      keywords= "slikio,SlikIO,slik.io")