# Copyright 2013 Sven Bartscher
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

# This file is part of cursgame 0.1.1
from distutils.core import setup

short_desc = "An easy interface for writing games using curses."
desc = """This package provides an API to curses,
       specialised for writing rogue-likes."""
classis = ['Development Status :: 4 - Beta',
           'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
           'Programming Language :: Python :: 3',
           'Topic :: Software Development :: Libraries :: Python Modules',
           'Topic :: Software Development :: User Interfaces',
           'Operating System :: POSIX',
           'Intended Audience :: Developers']

setup(name="cursgame",
      version="0.1.1",
      author="Sven Bartscher",
      author_email="sven.bartscher@weltraumschlangen.de",
      url="http://weltraumschlangen.de/programs/libraries/Cursgame",
      description=short_desc,
      long_description=desc,
      download_url="http://weltraumschlangen.de/programs/libraries/Cursgame/download.html",
      license="EUPL",
      package_dir={'cursgame': 'src'},
      packages=['cursgame'],
      classifiers=classis,
      platforms=['POSIX'])
      
