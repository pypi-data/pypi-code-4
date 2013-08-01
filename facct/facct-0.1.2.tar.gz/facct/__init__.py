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

r'''%(README)s

Example:

>>> import bench
>>> bench.main('corp_ref', False)
[OK] corp_ref 2014 init_year.
[OK] corp_ref 2014 already exists.
[OK] corp_ref 2016 init_year.
[OK] corp_ref 2016 already exists.
[OK] corp_ref 2010 account: no differences with benchmark
[OK] corp_ref 2011 account: no differences with benchmark
[OK] corp_ref 2012 account: no differences with benchmark
[OK] corp_ref 2013 account: no differences with benchmark
[OK] corp_ref 022013 bill.
[OK] corp_ref db.

You can also launch doctest with:
python facct/__init__.py -v

And distribution packaging with:
python setup.py sdist

More information on the distributable:
python setup.py --help
python setup.py --author
python setup.py --long-description
... and so forth
'''
import os
import facct.path_mngt as path_mngt

readme_file = os.path.join(path_mngt.get_dev_path(), 'README.txt')
if os.path.exists(readme_file):
    __doc__ = __doc__ % {'README': open(readme_file).read()}

license_name = 'GNU General Public License v3 or later (GPLv3+)'
__version__      = '0.1.2'
__author__       = 'Eric F.'
__author_email__ = 'efigue.foss@free.fr'
__url__          = 'http://eric.figuereo.free.fr'
__classifiers__  = '''
                   Development Status :: 3 - Alpha
                   Environment :: Console
                   Intended Audience :: Financial and Insurance Industry
                   License :: OSI Approved :: {0}
                   Operating System :: OS Independent
                   Programming Language :: Python
                   Programming Language :: Python :: 2
                   Programming Language :: Python :: 3
                   Natural Language :: English
                   Natural Language :: French
                   Topic :: Office/Business
                   Topic :: Office/Business :: Financial :: Accounting
                   '''.format(license_name)

__license__  = 'GPLV3+'

def _test():
    '''Run all doc tests of this module.'''
    import doctest
    return doctest.testmod()

if __name__ == '__main__':
    _test()

