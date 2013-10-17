#!/usr/bin/python
# -*-coding:utf8 -*
#
# Toolsbk is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

from setuptools import setup, find_packages
import toolsbk

setup(
        name = 'toolsbk',
        version = toolsbk.__version__,
        packages=find_packages(),
        author = 'Antoine Durand',
        author_email = 'antoinedurand.ad@gmail.com',
        description = 'Backup your usefull tools',
        long_description=open('README.rst').read(),
        url = 'https://gitorious.org/tools-backup/',
        entry_points = { 'console_scripts': ['toolsbk = toolsbk.toolsbk:toolsbk'] },
)


