#!/usr/bin/python
# Copyright (C) 2012 Brett Ponsler
# This file is part of pysiriproxy.
#
# pysiriproxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysiriproxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysiriproxy.  If not, see <http://www.gnu.org/licenses/>.
from sys import stderr
from os import environ
from os import listdir
from os.path import join, isfile
from setuptools import setup

setup(name='zopyx.pysiriproxy',
      version='0.2.0',
      description='Python implementation of SiriProxy.',
      maintainer='Andreas Jung',
      maintainer_email='andreas@andreas-jung.com',
      author='Brett Ponsler',
      author_email='ponsler@gmail.com',
      url='https://code.google.com/p/pysiriproxy/',
      packages=['pysiriproxy', 'pysiriproxy.connections',
                'pysiriproxy.objects', 'pysiriproxy.options',
                'pysiriproxy.plugins', 'pysiriproxy.testing'],
      include_package_data=True,
      license='GNU GPL v3',
      install_requires=[
        "biplist>=0.5",
        "twisted==12.1.0",
        "pyopenssl",
        "pyamp>=1.2",
        ],
       entry_points="""
       [console_scripts]
       siriproxy = pysiriproxy.cmdline:main
       """
      )
