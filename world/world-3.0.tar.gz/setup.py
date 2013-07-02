# Copyright (C) 2013 Barry A. Warsaw
#
# This file is part of world.
#
# world is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# world is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# world.  If not, see <http://www.gnu.org/licenses/>.

import distribute_setup
distribute_setup.use_setuptools()

from setup_helpers import get_version, require_python
from setuptools import setup, find_packages

require_python(0x20700f0)
__version__ = get_version('worldlib/__init__.py')


setup(
    name='world',
    version=__version__,
    description='world -- top level domain code mappings',
    author='Barry Warsaw',
    author_email='barry@python.org',
    license= 'GPLv3+',
    url='http://launchpad.net/world',
    keywords='domain name system DNS',
    packages= find_packages(),
    include_package_data=True,
    package_data={'': ['*.pck']},
    entry_points={
        'console_scripts': ['world = worldlib.__main__:main'],
        },
    test_suite='worldlib.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ]
    )
