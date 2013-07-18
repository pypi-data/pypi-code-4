import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mkbok",
    version = "0.0.2",
    author = "Larry Cai",
    author_email = "larry.caiyu@gmail.com",
    description = ("make markdown ebook"),
    license = "BSD",
    Platform = "Ubuntu",
    keywords = "markdown, ebook, pandoc",
    url = "https://github.com/larrycai/mkbok",
    packages=['mkbok'],
    long_description=read('README_python.mk'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
