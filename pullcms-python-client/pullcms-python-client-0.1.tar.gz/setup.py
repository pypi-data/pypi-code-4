# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="pullcms-python-client",
      version='0.1',
      description="Python API Client for the Pull4Up CMS",
      license="MIT",
      author="Pull4Up",
      author_email="fabiano.moraes@pull4up.com",
      url="https://github.com/Pull4up/cms-python-client",
      packages=find_packages(exclude=['tests']),
      keywords="pullcms cms python client",
      zip_safe=True)