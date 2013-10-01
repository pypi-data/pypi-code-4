#!/usr/bin/env python
from setuptools import setup, find_packages

from trebuchet.lib import get_version

setup(
    name = "le-trebuchet",
    packages = find_packages(),
    version = get_version(),
    url = 'https://github.com/ops-hero/trebuchet',
    author = 'Arnaud Seilles',
    author_email = 'arnaud.seilles@gmail.com',
    description = "Yet another package building tool",
    long_description="Yet another package building tool",
    include_package_data = True,
    entry_points = {
        "console_scripts" : [ "trebuchet = "
            "trebuchet.run:main"]
    },
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Build Tools',
                   ],
    install_requires = open('requirements.pip').readlines(),
    dependency_links = ["http://c.pypi.python.org/simple"],
)
