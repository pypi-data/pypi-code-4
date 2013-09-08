#!/usr/bin/env python
from setuptools import setup

from gachette import get_version

setup(
    name = "la-gachette",
    packages = [ 'gachette', ],
    version = get_version(),
    url = '',
    author = 'Arnaud Seilles',
    author_email = 'arnaud.seilles@gmail.com',
    description = "Module to handle working copy and build of project.",
    long_description="Module to handle deployment and building of packages."
        "It will prepare working copy on lab/build machines with specific branches/PR."
        "It will then trigger the install/build process and setup proper stacks/packages release.",
    include_package_data = True,
    entry_points = {
        "console_scripts" : [ "gachette = "
            "gachette.fabfile:main"]
    },
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
    install_requires = open('requirements.pip').readlines(),
)
