import os
from distutils.core import setup
from distutils.command.install import install
from distutils.command.bdist_wininst import bdist_wininst
import subprocess


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyivi",
    version = "0.0.4",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Wrapper around the IVI-COM and IVI-C drivers"""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyivi-package",
    packages=['pyivi',
              'pyivi/ivicom',
              'pyivi/ivic',
              'pyivi/ivifactory'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
                      'comtypes',
                      'ctypes'
    ]
)