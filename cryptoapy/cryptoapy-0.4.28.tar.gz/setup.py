#!/usr/bin/env python
#-*- coding: utf-8 -*-
from distutils.core import setup, Extension, Command
from platform import architecture
import sys
import os
import platform
import glob
import subprocess as sub
import multiprocessing

major, minor = sys.version_info[:2]

if architecture()[0] == '32bit':
    arch = 'ia32'
    size = '4'
else:
    arch = 'amd64'
    size = '8'

try:
    import nose
except ImportError:
    nose = None


class TestCommand(Command):
    """Custom distutils command to run the test suite."""

    user_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """Run the test suite with nose."""
        if not nose:
            print('W: nose package not found')
            return True
        return nose.core.run(argv=["", '-v', os.path.join(self._dir, 'tests')])


class SWIGCommand(Command):
    """Custom distutils command to generate wrappers"""

    user_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """Generate wrappers"""
        for arch, size in [('ia32', 4), ('amd64', 8)]:
            swig_cmd = [
                'swig',
                '-python',
                '-py3',
                '-builtin',
                '-c++',
                '-o',
                'cprocsp/csp_wrap_{0}.cxx'.format(arch),
                '-I./cpp/include',
                '-I./cprocsp',
                '-I./',
                '-DSIZEOF_VOID_P={0}'.format(size),
                'cprocsp/csp.i',
            ]
            sub.call(swig_cmd)

cmdclass = {'test': TestCommand,
            'swig': SWIGCommand}

include_dirs = ['cpp/include']
library_dirs = ['cpp']
libraries = []
extra_compile_args = ['-DSIZEOF_VOID_P={0}'.format(size)]

#extra_compile_args.append('-DDEBUG_LOG')

if platform.system() == 'Windows':
    include_dirs += [
        './',
        './cprocsp/',
    ]
    libraries += ['crypt32', 'pthread']
else:
    include_dirs += [
        '/opt/cprocsp/include',
        '/opt/cprocsp/include/cpcsp',
        '/opt/cprocsp/include/asn1c/rtsrc',
        '/opt/cprocsp/include/asn1data',
    ]
    library_dirs += ['/opt/cprocsp/lib/{0}'.format(arch)]
    libraries += ['asn1data',
                  'ssp',
                  'capi20']
    extra_compile_args += [
        '-DUNIX',
        '-DHAVE_LIMITS_H',
        '-DHAVE_STDINT_H',
        '-DCP_IOVEC_USE_SYSTEM',
    ]


sources = ['cprocsp/csp_wrap_{0}.cxx'.format(arch)]
sources.extend(glob.glob('cpp/src/*.cpp'))

csp = Extension('cprocsp._csp',
                sources=sources,
                include_dirs=include_dirs,
                library_dirs=library_dirs,
                libraries=libraries,
                extra_compile_args=extra_compile_args,)


setup(name='cryptoapy',
      version='0.4.28',
      author='Andrew Rodionoff',
      author_email='andviro@gmail.com',
      license='LGPL',
      platforms=['Linux', 'Windows'],
      install_requires=['pyasn1', 'pyasn1_modules'],
      ext_modules=[csp],
      description='Python/C++ wrapper for Microsoft cryptoapi services (currently, Russian GOST algorithms only)',
      packages=['cprocsp'],
      py_modules=['cprocsp.csp', 'cprocsp.rdn', 'cprocsp.cryptoapi',
                  'cprocsp.filetimes'],
      cmdclass=cmdclass,
      )
