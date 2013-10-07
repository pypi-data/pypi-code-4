#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1.2"


def read_long_description(filename="README.rst"):
    with open(filename) as f:
        return f.read().strip()


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()

setup(
    name="Minos",
    version=__version__,
    author="Kevin Novak",
    author_email="kevin@uber.com",
    url="https://github.com/uber/minos",
    packages=find_packages(),
    keywords=["tests", "validation"],
    description="Minos is a library to do flexible validation of Python objects",
    long_description=read_long_description(),
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
