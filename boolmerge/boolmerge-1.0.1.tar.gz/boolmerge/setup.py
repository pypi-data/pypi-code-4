# Boolmerge - Tools for merging sorted iterables with boolean operators.
# Copyright (C) 2013 Michaël Meyer

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


from os.path import join, dirname, abspath
from distutils.core import setup, Extension

with open(join(dirname(abspath(__file__)), "README.rst")) as f:
    long_description = f.read()

module = Extension('boolmerge', sources = ['boolmergemodule.c'])

setup (
    name = 'BoolMerge',
    version = '1.0',
    description = 'Tools for merging sorted iterables with boolean operators',
    long_description = long_description,
    author='Michaël Meyer',
    author_email='michaelnm.meyer@gmail.com',
    url='https://github.com/doukremt/boolmerge',
    ext_modules = [module],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: C',
        'Programming Language :: Python',
    )
)
