#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
pass

# Third-Party Libraries
import setuptools

try:
    import about # setup only, not a runtime dependency.
except ImportError:
    setuptools.Distribution().fetch_build_eggs("about")


metadata = about.get_metadata("logfile.py")

contents = dict(
  py_modules = ["logfile"],
)

requirements = dict()

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)

if __name__ == "__main__":
    setuptools.setup(**info)

