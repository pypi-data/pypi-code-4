#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="slikio-python",
      version="0.0.3",
      description="Python library for SlikIO - Charts for developers",
      long_description= "The source is on GitHub: http://github.com/SlikIO/slikio-python. Feel free to send me questions or feature requests to <daniel@slik.io>.",
      license="MIT",
      install_requires=["requests"],
      author="Daniel Brodsky, SlikIO",
      author_email="daniel@slik.io",
      url="http://slik.io",
      packages = ["slikio"],
      keywords= "slikio,SlikIO,slik.io, charts, graphs, django chart templates")