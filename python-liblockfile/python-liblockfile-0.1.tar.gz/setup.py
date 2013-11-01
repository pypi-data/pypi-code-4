# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for python-liblockfile."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type

from setuptools import setup


setup(
    name='python-liblockfile',
    author='Gavin Panella',
    author_email='gavin.panella@canonical.com',
    url='https://launchpad.net/python-liblockfile',
    version="0.1",
    packages={b'liblockfile'},
    package_dir={'liblockfile': 'liblockfile'},
    tests_require={"testtools >= 0.9.32", "fixtures >= 0.3.14"},
    test_suite="liblockfile.tests",
    include_package_data=True,
    zip_safe=False,
    description="A wrapper around liblockfile, using ctypes.",
)
