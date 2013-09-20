#!python

# Thanks to beautiful setuptools package <http://peak.telecommunity.com/DevCenter/setuptools>

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "aDict2",
    version = "0.1.0",
    packages = find_packages(),
    package_data = {
        '': ['*.txt'],
    },

    # metadata for upload to PyPI
    author = "arseniiv",
    author_email = "arseniiv@gmail.com",
    description = "aDict dictionary format handling",
    long_description = open('README.txt').read(),
    license = "CC0",
    keywords = "dictionary text",
    url = "http://arseniiv.info/progr/adict",
)