# -*- coding: utf-8 -*-
"""
pnw
===
"""
import os
import imp
from setuptools import setup

def get_version():
    " Get version & version_info without importing pnw.__init__ "
    path = os.path.join(os.path.dirname(__file__), 'pnw')
    fp, pathname, desc = imp.find_module('pnw', [path])
    try:
        v = imp.load_module('pnw', fp, pathname, desc)
        return v.version
    finally:
        fp.close()

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = get_version()

setup(name='pnw',
      version=version,
      license='Apache 2.0',
      author='Matthias Lesch',
      author_email='ml@matthiaslesch.de',
      description='A text processing and literate programming tool inspired by antiweb, noweb',
      long_description=read("README.rst"),
      include_package_data=True,
      packages=['pnw'],
      scripts=['scripts/pnw'],
      )

