#!/usr/bin/env python
from setuptools import setup


setup(
    name="hurler",
    version="0.1.0",
    license="BSD",
    description="A simple callback mechanism with decorated filters.",
    author="Wesley Bitter",
    author_email="hurler@wessie.info",
    url="http://github.com/Wessie/hurler/",
    packages=["hurler"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
