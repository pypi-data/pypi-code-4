#!/usr/bin/env python

from __future__ import absolute_import

from distutils.command.build_py import build_py as _build_py
import doctest as _doctest

class doctest(_build_py):

    description = 'Run doctests'

    def run(self):
        from distcontrib.tools import find_package_sources
        from setuptools import find_packages
        from distutils.util import convert_path
        # distutils uses old-style classes, so no super()
        _build_py.run(self)
        # now run doctest
        for package in self.distribution.packages:
            for dummy, sources in find_package_sources(package).items():
                for source in sources:
                    _doctest.testfile(source, False)
