#!/usr/bin/env python

"""The usual package management stuff."""

from setuptools import setup


setup(
    name="ook",
    author="Zero Piraeus",
    author_email="z@etiol.net",
    description=open("ook/__init__.py").readlines()[0].strip('"\n'),
    install_requires=["six"],
    keywords="version sensitive monkey patch",
    license="GPLv3",
    long_description=open("README").read(),
    packages=["ook"],
    setup_requires=["setuptools_hg"],
    url="https://bitbucket.org/schesis/ook",
    version=open("ook/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
)
