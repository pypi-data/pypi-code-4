# This file is part of ngs_plumbing.

# ngs_plumbing is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ngs_plumbing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2012 Laurent Gautier

import os, sys

try:
    from setuptools import setup
    setup_opts = {'entry_points':
                      """
[console_scripts]
xsq-convert = ngs_plumbing.xsqconvert:main
xsq-report = ngs_plumbing.xsqconvert:htmlreport
cs-code = ngs_plumbing.colorspace:exec_code
""",
                  'zip_safe': False}
except ImportError:
    from distutils.core import setup
    if sys.platform == 'win32':
        print('Note: without Setuptools installed you will have to use "python -c \'import ngs_plumbing.colorspace as cs; cs.exec_code()\'"')
        setup_opts = {}
    else:
        setup_opts = {'scripts': ['scripts/xsq-convert',
                                  'scripts/xsq-report',
                                  'scripts/cs-code']}


#from distutils.ccompiler import get_default_compiler
#from distutils.ccompiler import new_compiler

from distutils.extension import Extension
from src.__init__ import __version__

srcpath = 'src'

srcpath_data = os.path.join(srcpath, 'data')
xsq_files = tuple(os.path.join(path,f) \
                      for path,dirs,files in os.walk(srcpath_data, '.xsq') \
                      for f in files if f.endswith('.xsq'))

html_files = tuple(os.path.join(path,f) \
                       for path,dirs,files in os.walk(os.path.join(srcpath_data, 'html'), '.html') \
                       for f in files if f.endswith('.html'))

js_files = tuple(os.path.join(path,f) \
                     for path,dirs,files in os.walk(os.path.join(srcpath_data, 'html'), '.js') \
                     for f in files if f.endswith('.js'))

other_files = (os.path.join(srcpath_data, 'reads.fq'),)

package_data = list(x.split(os.path.sep, 1)[1] for x in xsq_files) + \
    list(x.split(os.path.sep, 1)[1] for x in html_files) + \
    list(x.split(os.path.sep, 1)[1] for x in js_files) + \
    list(x.split(os.path.sep, 1)[1] for x in other_files)

cython_ext = 'c'

ext_modules = [Extension(name = "ngs_plumbing.%s" %x, 
                         sources = [os.path.join(srcpath, 
                                                 '%s.%s' %(x, cython_ext))],
                         include_dirs = ['.'],
                         depends = [os.path.join(srcpath, '_libdna.h', 'bitpack.h')],
                         extra_compile_args = ['-Wall', '-O3', '-funroll-loops'],
                         extra_link_args = ['-g']) for x in ('_libxsq', '_libdna', '_libdnaqual')]



setup(name = 'ngs_plumbing',
      description = 'Plumbing for NGS data',
      ext_modules = ext_modules,
      author = 'Laurent Gautier',
      author_email = 'lgautier@gmail.com',
      classifiers = ['Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 3',
                     'License :: OSI Approved :: GNU Affero General Public License v3',
                     'License :: Free for non-commercial use',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'Development Status :: 4 - Beta'
                     ],
      version = __version__,
      requires = ['jinja2', ],
      packages = ['ngs_plumbing', ],
      package_dir = {'ngs_plumbing': 'src'},
      package_data = {'ngs_plumbing': package_data},
      headers = [os.path.join(srcpath, '_libdna.h'),],
      **setup_opts)

try:
    import h5py
except ImportError as ie:
    import sys
    sys.stderr.write("\nWarning: The Python package 'h5py' cannot be imported.\n")
    sys.stderr.write("Without it, capabilities related to the XSQ format cannot be used.\n")
    sys.stderr.flush()
