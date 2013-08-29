import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dfutils",
    version = "0.0.1",
    author = "Claudiu Saftoiu",
    author_email = "csaftoiu@gmail.com",
    description = ("Utilities to work with Twisted Deferreds."),
    license = "Public Domain",
    keywords = "twisted deferred utils",
    url = "http://pypi.python.org/pypi/dfutils",
    packages=['dfutils'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Framework :: Twisted",
        "License :: Public Domain",
    ],
)
