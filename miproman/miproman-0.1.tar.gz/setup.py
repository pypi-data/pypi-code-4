#!/usr/bin/env python

import os
import re
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    sys.exit("""\nError: Setuptools is required for installation.
    -> http://pypi.python.org/pypi/setuptools
    or http://pypi.python.org/pypi/distribute\n""")


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
info = open(os.path.join(here, "miproman", "__init__.py")).read()
VERSION = re.compile(r'.*__version__ = "(.*?)"', re.S).match(info).group(1)


setup(
    name="miproman",
    version=VERSION,
    description="Easy iTerm2 Profiles For Everyone!",
    # long_description=README,
    author="Jatin Nagpal",
    author_email="jatinn@outlook.com",
    url="https://github.com/jatinn/miproman",
    download_url="https://github.com/jatinn/miproman/tarball/0.1",
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=[
        "argparse",
        "biplist",
    ],
    entry_points = dict(
        console_scripts=[
            "add_profile = miproman:main",
        ]
    ),
    include_package_data=True,
    zip_safe=True,
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Terminals",
        "Topic :: System",
        "Topic :: Utilities",
    ),
)
