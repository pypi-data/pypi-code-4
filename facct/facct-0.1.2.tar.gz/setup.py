#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools
import re
import facct as package

setuptools.setup(
    name                 = package.__name__,
    version              = package.__version__,
    description          = package.__doc__.partition('\n\n')[0],
    long_description     = package.__doc__.partition('\n\n')[2],
    author               = package.__author__,
    author_email         = package.__author_email__,
    license              = package.__license__,
    url                  = package.__url__,
    classifiers          = re.findall(r'\S[^\n]*', package.__classifiers__),
    packages             = setuptools.find_packages(),
    include_package_data = True,
    zip_safe             = True,
    install_requires     = ['pysqlite'],
)
