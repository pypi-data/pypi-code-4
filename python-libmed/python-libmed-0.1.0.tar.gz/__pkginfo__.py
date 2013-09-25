# Copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of python-libmed.
#
# python-libmed is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# python-libmed is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with python-libmed.  If not, see <http://www.gnu.org/licenses/>.

"""python-libmed packaging information"""

from distutils.extension import Extension

modname = distname = "python-libmed"

numversion = (0, 1, 0)
version = '.'.join([str(num) for num in numversion])

license = 'LGPL'

description="Manipulation of MED files."

web = "https://www.logilab.org/project/python-libmed"
mailinglist = "mailto://python-projects@lists.logilab.org"

author="Logilab S.A. (Paris, France)"
author_email="contact@logilab.fr"

classifiers=[
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
  "Programming Language :: Python",
  "Programming Language :: Cython",
  "Topic :: Scientific/Engineering",
  "Topic :: Scientific/Engineering :: Physics",
  "Topic :: Software Development :: Libraries :: Python Modules"],

debian_maintainer = "Denis Laxalde"
debian_maintainer_email = "denis.laxalde@logilab.fr"

packages     = ['libmed']
package_data = {'libmed': ['doc/*']}

ext_modules=[
    Extension("libmed._file", ["libmed/_file.pyx"],
              libraries=["medC"]),
    Extension("libmed._mesh", ["libmed/_mesh.pyx"],
              libraries=["medC"]),
    Extension("libmed._field", ["libmed/_field.pyx"],
              libraries=["medC"]),
    Extension("libmed._parameter", ["libmed/_parameter.pyx"],
              libraries=["medC"]),
    Extension("libmed._profile", ["libmed/_profile.pyx"],
              libraries=["medC"]),
    Extension("libmed._medtypes", ["libmed/_medtypes.pyx"],
              libraries=["medC"]),
    Extension("libmed._utils", ["libmed/_utils.pyx"],
              libraries=["medC"])
]
