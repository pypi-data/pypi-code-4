#! /usr/bin/python

from setuptools.command import easy_install
from setuptools import setup, find_packages
import shutil
import os.path
import sys
import hashlib

PKG_DIR = os.path.abspath(os.path.dirname(__file__))

# Make it possible to overide script wrapping
old_is_python_script = easy_install.is_python_script
def is_python_script(script_text, filename):
    if 'SETUPTOOLS_DO_NOT_WRAP' in script_text:
        return False
    return old_is_python_script(script_text, filename)
easy_install.is_python_script = is_python_script

setup(
    name = "virtualenvtools",
    description = "Command line tools to make virtualenvs slightly nicer.",
    keywords = "virtualenv",
    install_requires = [],
    version = "0.0.1",
    author = "RedHog (Egil Moeller)",
    author_email = "egil@skytruth.org",
    license = "GPL",
    url = "http://github.com/redhog/virtualenvtools",
    packages = find_packages(),
    package_data = {'': ['*.txt', '*.css', '*.html', '*.js']},
    include_package_data = True,
    scripts = ['list-manually-installed-packages', 'runinvirtualenv']
)
