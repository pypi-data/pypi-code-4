import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "jsonprop",
    version = "0.0.5",
    author = "Dan Newcome",
    author_email = "dnewcome@circleup.com",
    description = ("A json serialization library for python."),
    license = "BSD",
    keywords = "json serialization",
    url = "http://packages.python.org/jsonprop",
    packages=['jsonprop'],
    long_description = read('README'),
    install_requires = [],
    classifiers = [
        "Development Status :: 3 - Alpha",
	"Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: BSD License",
    ],
)
