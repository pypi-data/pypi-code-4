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

from distutils.core import setup
from Cython.Distutils import build_ext

from __pkginfo__ import (distname, version, license, description, web, author,
                         author_email, classifiers, packages, package_data,
                         ext_modules)


setup(name=distname,
      version=version,
      license=license,
      author=author,
      author_email=author_email,
      url=web,
      description=description,
      long_description=file("README").read(),
      classifiers=classifiers,
      cmdclass={"build_ext": build_ext},
      ext_modules=ext_modules,
      packages=packages,
      package_data=package_data)
