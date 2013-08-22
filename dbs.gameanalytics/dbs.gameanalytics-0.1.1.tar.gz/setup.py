#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dbs.gameanalytics",
    namespace_packages=['dbs'],
    version="0.1.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},

    # egg params
    zip_safe=True,
    include_package_data=False,

    # metadata for upload to PyPI
    license="BSD",
    author="Domantas Jackūnas",
    author_email="devops@dreambitstudios.com",
    description=("Http://GameAnalytics.com REST API implementation"),
    url="http://www.dreambitstudios.com",
    keywords="utilities color log",
    long_description=read('README.rst'),

    classifiers=[
        "Topic :: Utilities",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python",
    ],
)
