__license__ = '''
This file is part of Dominate.

Dominate is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

Dominate is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General
Public License along with dominate.  If not, see
<http://www.gnu.org/licenses/>.
'''

# http://guide.python-distribute.org/creation.html
from setuptools import setup

version = '2.0.0'

setup(
  name    = 'dominate',
  version = version,
  author  = 'Tom Flanagan and Jake Wharton',
  author_email = 'tom@zkpq.ca',
  license = 'LICENSE.txt',

  url          = 'http://github.com/Knio/dominate/',

  description      = 'Dominate is a Python library for creating and manipulating HTML documents using an elegant DOM API.',
  keywords         = 'framework templating template html xhtml python html5',

  classifiers = [
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Intended Audience :: Developers',
  ],
  packages = ['dominate'],
  install_requires = [],
  include_package_data = True,
)
