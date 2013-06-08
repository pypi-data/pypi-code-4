#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import yworklog
import sys

setup(
    name='yworklog',
    version=yworklog.__version__,
    description='YWorkLog',
    author='Jan Matejka',
    author_email='yac@blesmrt.net',
    url='https://github.com/yaccz/worklog',

    packages = find_packages(
        where = '.'
    ),

    install_requires = [
        "cement",
        "setuptools",
        "sqlalchemy",
        "pyxdg",
        "pysqlite",
        "alembic",
    ],

    entry_points = {
        'console_scripts': ['wl = yworklog.core:main']},

    data_files = [
        ('yworklog/git-hooks', ['git-hooks/prepare-commit-msg'])
    ]
)
