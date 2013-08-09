#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Wu Liang
@contact: garcia.wul@alibaba-inc.com
@date: 13-8-8
@version: 0.0.0
"""

import os
import shutil
from setuptools import setup
from setuptools import Command

version = '0.0.2'


class CleanCommand(Command):
    description = "clean build directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        if os.path.exists(os.path.join(os.path.dirname(__file__), "build")):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), "build"))
        if os.path.exists(os.path.join(os.path.dirname(__file__), "dist")):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), "dist"))
        if os.path.exists(os.path.join(os.path.dirname(__file__), "xlogin.egg-info")):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), "xlogin.egg-info"))

setup(name = 'xlogin',
    version = version,
    description = "ssh登陆管理工具",
    long_description = "",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: Freely Distributable",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.5",
        "Topic :: Utilities",
    ],
    keywords = ("ssh", "ssh管理"),
    author = 'magicsky',
    author_email = 'garcia.relax@gmail.com',
    url = 'https://github.com/magicsky/xlogin',
    license = 'BSD',
    scripts = [
        "bin/xlogin",
        "bin/xlogin-service",
    ],
    install_requires = [
      "demjson >= 1.6",
      "Mako >= 0.8.1",
      "paramiko >= 1.11.0",
      "PyYAML >= 3.10",
      "Flask >= 0.10.1",
    ],
    cmdclass = {
        "clean": CleanCommand
    }
)