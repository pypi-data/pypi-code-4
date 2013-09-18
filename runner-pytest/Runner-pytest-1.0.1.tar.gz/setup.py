#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
#   Author(s): Milan Falesnik   <milan@falesnik.net>
#                               <mfalesni@redhat.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from setuptools import setup
import os


setup(
    name="Runner-pytest",
    version="1.0.1",
    author="Milan Falešník",
    author_email="milan@falesnik.net",
    description="Simple command runner - fixture provider for py.test",
    license="GPLv2",
    keywords="run command bash shell",
    url="https://github.com/mfalesni/Runner",
    py_modules=['runner_pytest_plugin'],
    entry_points = {'pytest11': ['runner_pytest_plugin = runner_pytest_plugin']},
    install_requires = ['Runner>=1.0', 'pytest>=2.2.4'],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Unix Shell"
    ]
)
