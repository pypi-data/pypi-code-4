# -*- coding: utf-8 -*-

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "foxInstaller",
    version = "0.1.6",
    author = "Jyrno Ader",
    author_email = "jyrno42@gmail.com",
    description = ("A simple installation script for my own django projects."),
    license = "BSD",
    keywords = "foxInstaller django jyrno42",
    url = "http://th3f0x.com",
    packages=['foxInstaller'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)