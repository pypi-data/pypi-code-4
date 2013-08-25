#!/usr/bin/env python
"""
python-aop is part of LemonFramework.

python-aop is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python-aop is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with python-aop. If not, see <http://www.gnu.org/licenses/>.


Copyright (c) 2013 Vicente Ruiz <vruiz2.0@gmail.com>
"""
import os
from distutils.core import setup
from aop import version_info


setup(
    name='python-aop',
    version='.'.join(str(s) for s in version_info),
    description='Python AOP Framework',
    author='Vicente Ruiz Rodríguez',
    author_email='vruiz2.0@gmail.com',
    url='https://github.com/LemonFramework/python-aop',
    license='GPLv3',
    packages=['aop', 'tests'],
    keywords = 'aop',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
