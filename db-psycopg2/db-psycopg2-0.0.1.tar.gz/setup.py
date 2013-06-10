#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages


if __name__ == "__main__":
    setup(name="db-psycopg2",
          version="0.0.1",
          description="psycopg2 driver for db",
          author="John Evans",
          author_email="lgastako@gmail.com",
          url="https://github.com/lgastako/db-psycopg2",
          install_requires=["db", "psycopg2"],
          py_modules=["db_psycopg2"],
          provides=["db_psycopg2"])
