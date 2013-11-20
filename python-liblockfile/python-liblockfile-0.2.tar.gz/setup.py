# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for python-liblockfile."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type

from sys import version_info

from setuptools import setup


setup(
    name='python-liblockfile',
    author='Gavin Panella',
    author_email='gavin.panella@canonical.com',
    url='https://launchpad.net/python-liblockfile',
    version="0.2",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    packages={b'liblockfile' if version_info.major == 2 else 'liblockfile'},
    package_dir={'liblockfile': 'liblockfile'},
    tests_require={"testtools >= 0.9.32", "fixtures >= 0.3.14"},
    test_suite="liblockfile.tests",
    description="A wrapper around liblockfile, using ctypes.",
)
