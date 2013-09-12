#! /usr/bin/env python

from distutils.core import setup

import sqlliterals

setup(
    name         = "sqlliterals",
    description  = "SQL statement tokenisation for the detection of literal regions.",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.python.org/pypi/sqlliterals",
    version      = sqlliterals.__version__,
    packages     = ["sqlliterals"]
    )
