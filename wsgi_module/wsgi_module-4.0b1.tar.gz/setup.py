from __future__ import print_function

import os
import sys
import fnmatch
import subprocess

from setuptools import setup
from distutils.core import Extension
from distutils.sysconfig import get_config_var as get_python_config
from distutils.sysconfig import get_python_lib

# Compile all available source files.

source_files = [name for name in 
        os.listdir(os.path.dirname(os.path.abspath(__file__)))
        if fnmatch.fnmatch(name, '*.c')]

# Work out all the Apache specific compilation flags.

def find_program(names, default=None, paths=[]):
    for name in names:
        for path in os.environ['PATH'].split(':') + paths:
            program = os.path.join(path, name)
            if os.path.exists(program):
                return program
    return default

APXS = os.environ.get('APXS')

if APXS is None or not os.path.abspath(APXS):
    APXS = find_program(['apxs2', 'apxs'], 'apxs', ['/usr/sbin'])

def get_apxs_config(query):
    p = subprocess.Popen([APXS, '-q', query],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if isinstance(out, bytes):
        out = out.decode('UTF-8')
    return out.strip()

INCLUDEDIR = get_apxs_config('INCLUDEDIR')
CPPFLAGS = get_apxs_config('CPPFLAGS').split()
CFLAGS = get_apxs_config('CFLAGS').split()

EXTRA_INCLUDES = get_apxs_config('EXTRA_INCLUDES').split()
EXTRA_CPPFLAGS = get_apxs_config('EXTRA_CPPFLAGS').split()
EXTRA_CFLAGS = get_apxs_config('EXTRA_CFLAGS').split()

# Write out apxs_config.py which caches various configuration
# related to Apache.

BINDIR = get_apxs_config('BINDIR')
SBINDIR = get_apxs_config('SBINDIR')

PROGNAME = get_apxs_config('PROGNAME')

MPM_NAME = get_apxs_config('MPM_NAME')
LIBEXECDIR = get_apxs_config('LIBEXECDIR')
SHLIBPATH_VAR = get_apxs_config('SHLIBPATH_VAR')

if os.path.exists(os.path.join(SBINDIR, PROGNAME)):
    HTTPD = os.path.join(SBINDIR, PROGNAME)
elif os.path.exists(os.path.join(BINDIR, PROGNAME)):
    HTTPD = os.path.join(BINDIR, PROGNAME)
else:
    HTTPD = PROGNAME

with open(os.path.join(os.path.dirname(__file__),
        'apxs_config.py'), 'w') as fp:
    print('HTTPD = "%s"' % HTTPD, file=fp)
    print('BINDIR = "%s"' % BINDIR, file=fp)
    print('SBINDIR = "%s"' % SBINDIR, file=fp)
    print('PROGNAME = "%s"' % PROGNAME, file=fp)
    print('MPM_NAME = "%s"' % MPM_NAME, file=fp)
    print('LIBEXECDIR = "%s"' % LIBEXECDIR, file=fp)
    print('SHLIBPATH_VAR = "%s"' % SHLIBPATH_VAR, file=fp)

# Work out location of Python library and how to link it.

PYTHON_VERSION = get_python_config('VERSION')
PYTHON_LDVERSION = get_python_config('LDVERSION') or ''

PYTHON_LIBDIR = get_python_config('LIBDIR')
PYTHON_CFGDIR =  get_python_lib(plat_specific=1, standard_lib=1) + '/config'

if PYTHON_LDVERSION and PYTHON_LDVERSION != PYTHON_VERSION:
    PYTHON_CFGDIR = '%s-%s' % (PYTHON_CFGDIR, PYTHON_LDVERSION)

PYTHON_LDFLAGS = ['-L%s' % PYTHON_LIBDIR, '-L%s' % PYTHON_CFGDIR]
PYTHON_LDLIBS = ['-lpython%s' % PYTHON_LDVERSION]

if os.path.exists(os.path.join(PYTHON_LIBDIR,
        'libpython%s.a' % PYTHON_VERSION)):
    PYTHON_LDLIBS = ['-lpython%s' % PYTHON_VERSION]

if os.path.exists(os.path.join(PYTHON_CFGDIR,
        'libpython%s.a' % PYTHON_VERSION)):
    PYTHON_LDLIBS = ['-lpython%s' % PYTHON_VERSION]

# Create the final set of compilation flags to be used.

INCLUDE_DIRS = [INCLUDEDIR]
EXTRA_COMPILE_FLAGS = (EXTRA_INCLUDES + CPPFLAGS + EXTRA_CPPFLAGS +
        CFLAGS + EXTRA_CFLAGS)
EXTRA_LINK_ARGS = PYTHON_LDFLAGS + PYTHON_LDLIBS

# Force adding of LD_RUN_PATH for platforms that may need it.

LD_RUN_PATH = os.environ.get('LD_RUN_PATH', '')
LD_RUN_PATH += ':%s:%s' % (PYTHON_LIBDIR, PYTHON_CFGDIR)
LD_RUN_PATH = LD_RUN_PATH.lstrip(':')

os.environ['LD_RUN_PATH'] = LD_RUN_PATH

# Now add the definitions to build everything.

extension_name = 'mod_wsgi-py%s%s' % sys.version_info[:2]

extension = Extension(extension_name, source_files,
        include_dirs=INCLUDE_DIRS, extra_compile_args=EXTRA_COMPILE_FLAGS,
        extra_link_args=EXTRA_LINK_ARGS)

setup(name = 'wsgi_module',
    version = '4.0b1',
    description = 'Installer for Apache/mod_wsgi.',
    author = 'Graham Dumpleton',
    author_email = 'Graham.Dumpleton@gmail.com',
    license = 'Apache',
    py_modules = ['wsgi_module', 'apxs_config'],
    ext_modules = [extension],
    entry_points = { 'console_scripts': ['wsgi-admin = wsgi_module:main'],},
)
