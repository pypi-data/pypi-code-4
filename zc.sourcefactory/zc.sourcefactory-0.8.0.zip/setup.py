##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
version = '0.8.0'

from setuptools import setup, find_packages
import os.path

def read_file(*args):
    path = os.path.join(os.path.dirname(__file__), *args)
    file_contents = open(path, "r").read()
    return file_contents + "\n\n"

setup(
    name="zc.sourcefactory",
    version=version,
    author="Zope Corporation and Contributors",
    author_email="zope-dev@zope.org",
    url="http://pypi.python.org/pypi/zc.sourcefactory",
    keywords="zope zope3 vocabulary source factory",
    description="An easy way to create custom Zope 3 sources.",
    license="ZPL 2.1",
    long_description=(
        read_file("src", "zc", "sourcefactory", "README.txt") +
        read_file("src", "zc", "sourcefactory", "mapping.txt") +
        read_file("src", "zc", "sourcefactory", "constructors.txt") +
        read_file("src", "zc", "sourcefactory", "adapters.txt") +
        read_file("src", "zc", "sourcefactory", "browser", "README.txt") +
        read_file("src", "zc", "sourcefactory", "browser", "token.txt") +
        read_file("CHANGES.txt")
        ),
    classifiers = [
        "Topic :: Software Development",
        "Framework :: Zope3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: Zope Public License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],

    packages=find_packages('src'),
    package_dir={'':'src'},

    include_package_data=True,
    install_requires=[
        "setuptools",
        "ZODB3",
        "zope.intid",
        "zope.browser",
        "zope.component",
        "zope.dublincore",
        "zope.interface",
        "zope.proxy",
        "zope.publisher",
        "zope.schema",
        ],
    namespace_packages=['zc'],
    extras_require={
        "test": ["zope.testing",
                 "zope.app.testing",
                 "zope.keyreference",
                 "zope.app.zcmlfiles",
                 ]},
    zip_safe=False,
    )
