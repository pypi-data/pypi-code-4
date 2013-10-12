# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
INSTALL_REQUIREMENTS = [str(r.req) for r in parse_requirements("requirements/production.txt")]
TEST_REQUIREMENTS = [str(r.req) for r in parse_requirements("requirements/test.txt")]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-conntrackt',
    version='0.1',
    packages=find_packages(exclude=["projtest", "projtest.*"]),
    include_package_data=True,
    license='GPLv3+',
    description='A simple application for tracking connection requirements between different entities in a network.',
    long_description=README,
    url='http://projects.majic.rs/conntrackt',
    author='Branko Majic',
    author_email='branko@majic.rs',
    install_requires=INSTALL_REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: System :: Networking :: Firewalls',
    ],
)
