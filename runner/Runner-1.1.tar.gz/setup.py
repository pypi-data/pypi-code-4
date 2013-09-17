#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
#   Author(s): Milan Falesnik   <milan@falesnik.net>
#                               <mfalesni@redhat.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from setuptools import setup
import os



setup(
    name="Runner",
    version="1.1",
    author="Milan Falešník",
    author_email="milan@falesnik.net",
    description="Simple command runner",
    license="GPLv2",
    keywords="run command bash shell",
    url="https://github.com/mfalesni/Run",
    packages=["Runner"],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Unix Shell"
    ]
)
