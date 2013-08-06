#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

    
setup(
    name = "snakeriver",
    version = "0.1.2",
    author = "Andrew Zhabinski",
    author_email = "faithlessfriend@gmail.com",
    description = ("Another way to think about Hadoop Streaming in Python"),
    license = "MIT",
    keywords = "hadoop streaming",
    url = "https://github.com/faithlessfriend/snakeriver",
    packages=['snakeriver'],
    long_description=read('README')
)