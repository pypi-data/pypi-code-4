# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).
from setuptools import setup, find_packages

from ssoclient import __version__

setup(
    name='ssoclient',
    version=__version__,

    author='Canonical ISD Hackers',
    author_email='canonical-isd@lists.launchpad.net',

    license='AGPLv3',

    packages=find_packages(),
    install_requires=[
        'requests-oauthlib',
        'requests',
    ],

    tests_require=[
        'mock',
    ],
    test_suite='ssoclient.tests',
)
