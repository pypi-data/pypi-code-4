# -*- coding: utf-8 -*-

from setuptools import setup
from io import open

classifiers = (
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
)

long_description = open("README.rst", encoding='utf-8').read().encode('ascii', 'ignore')

setup(
    name = "wikipedia",
    version = "0.9",
    author = "Jonathan Goldsmith",
    author_email = "jhghank@gmail.com",
    description = "Wikipedia API for Python",
    license = "MIT",
    keywords = "python wikipedia API",
    url = "https://github.com/goldsmith/Wikipedia",
    packages = ['wikipedia', 'tests'],
    long_description = long_description,
    classifiers = classifiers,
)