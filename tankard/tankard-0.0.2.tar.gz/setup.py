#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages


if __name__ == "__main__":
    setup(name="tankard",
          version="0.0.2",
          description="tankard",
          author="John Evans",
          author_email="lgastako@gmail.com",
          url="https://github.com/lgastako/tankard",
          install_requires=[
              "flask",
          ],
          packages=find_packages(),
          provides=["tankard"])
