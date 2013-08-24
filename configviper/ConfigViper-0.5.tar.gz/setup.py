# -*- coding: utf-8 -*-
#
# setup.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2012  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

from distutils.core import setup

with open('README.txt') as f:
    long_description = f.read()

with open('VERSION') as f:
    version = f.read().replace('\n', '')

setup(name='ConfigViper',
        version=version,
        description='Handles configuration saved as JSON files.',
        long_description=long_description,
        license='LGPL',
        author='Daniel Gonçalves',
        author_email='daniel@base4.com.br',
        url='https://bitbucket.org/danielgoncalves/configviper',
        packages=['configviper', 'configviper.lockfile',],
        classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Other Environment',
                'Intended Audience :: Developers',
                'Intended Audience :: System Administrators',
                'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries',
                'Topic :: Software Development :: Libraries :: Python Modules',])
