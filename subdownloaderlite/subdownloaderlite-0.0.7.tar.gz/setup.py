import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = __import__('subdownloader').get_version()

setup(
    name = "subdownloaderlite",
    version = version,
    author = "Gabriel Melillo",
    author_email = "gabriel@melillo.me",
    description = ("A simple command line tool to search and download subtitles from opensubtitles.org "),
    license = "BSD",
    url = "http://www.melillo.me/subdownloader",
    packages = ['subdownloader','subdownloader/subDownLib','subdownloader/util'],
    scripts = ['subdownloader-lite',],
)
