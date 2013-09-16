#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import cudapyint

try:
    from setuptools import setup, Extension
    setup, Extension
except ImportError:
    from distutils.core import setup, Extension
    setup, Extension

import numpy.distutils.misc_util


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


desc = open("README.rst").read()
required = ["numpy", "pycuda"]


setup(
    name="CudaPyInt",
    version=cudapyint.__version__,
    author=cudapyint.__author__,
    author_email="jakeret@phys.ethz.ch",
    url="http://www.fhnw.ch",
    license="GPLv3",
    packages=["cudapyint"],
    zip_safe=False,
    description="GPU based parallel ode solver",
    long_description=desc,
    install_requires=required,
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
    package_data={"": ["LICENSE"],
                  },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: C",
    ],
)
