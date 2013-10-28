#!/usr/bin/env python
from setuptools import setup


def get_version():
    with open("dotjs.py", "r") as fp:
        for line in fp:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])


def read(filename):
    with open(filename, "r") as fp:
        return fp.read()


setup(
    name="dotjs",
    version=get_version(),
    description="A Python implementation of the dotjs HTTP server",
    long_description=read("README.rst"),
    author="Paul Hooijenga",
    author_email="paulhooijenga@gmail.com",
    url="https://github.com/hackedd/python-dotjs",
    license="MIT",
    py_modules=["dotjs"],
    entry_points={
        "console_scripts": [
            "dotjs = dotjs:_main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
    ],
)
