import os
import sys

execfile('webalerts/version.py')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'webalerts',
    'webalerts.sites',
    'webalerts.notifications',
]

requires = [
    "requests >= 2.0.1",
    "lxml >= 3.2.3",
    "cssselect >= 0.9.1",
    "PyYAML >= 3.10",
    "pytz >= 2013.8",
]

setup(
    name = "webalerts",
    version = __version__,
    description = "WebAlerts is a Python package that lets you be notified for new website posts matching your regex patterns.",
    long_description = open("README.rst").read(),
    author = "Choongmin Lee",
    author_email = "choongmin@me.com",
    url = "https://github.com/clee704/WebAlerts",
    packages = packages,
    install_requires = requires,
    license = "MIT License",
    keywords = "web crawler notification",
    classifiers = [
        # Full list is here: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet",
    ],
)
