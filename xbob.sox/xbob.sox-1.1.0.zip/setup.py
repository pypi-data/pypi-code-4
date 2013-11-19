#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Elie Khoury <elie.khoury@idiap.ch>
# Thu Nov 14 22:20:38 CET 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Audio reader and writer using sox for bob and python
"""

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires='xbob.extension'))
from xbob.extension import Extension, build_ext

setup(

    name="xbob.sox",
    version="1.1.0",
    description="Audio reader and writer using sox for bob and python",
    license="GPLv3",
    author='Elie Khoury',
    author_email='elie.khoury@idiap.ch',
    long_description=open('README.rst').read(),
    url='http://pypi.python.org/pypi/xbob.sox',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages=[
      "xbob",
      ],

    install_requires=[
      'setuptools',
      'bob',
      ],

    entry_points = {
      'console_scripts': [
         ],
      'bob.test': [
         'sox = xbob.sox.test:SoxTest',
         ],
      },

    cmdclass = {
      'build_ext': build_ext,
      },

    ext_modules=[
      Extension("xbob.sox._ext", #new implementation
        [
          "xbob/sox/ext/ext.cc",
          "xbob/sox/ext/reader.cc",
          "xbob/sox/ext/writer.cc",
          "xbob/sox/ext/utilities.cc",
        ],
        pkgconfig = [
          "sox",
        ],
        ),
      ],

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],

)
