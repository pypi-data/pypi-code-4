#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="python-instagram-fc",
      version="0.8.0",
      description="Instagram API client",
      license="MIT",
      install_requires=["simplejson","httplib2"],
      author="Instagram, Inc",
      author_email="apidevelopers@instagram.com",
      url="http://github.com/futurecolors/python-instagram",
      packages = find_packages(),
      keywords= "instagram",
      zip_safe = True)
