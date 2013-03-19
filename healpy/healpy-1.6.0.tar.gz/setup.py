#!/usr/bin/env python

# Bootstrap distribute installation
from distribute_setup import use_setuptools
use_setuptools()

import os
from os.path import join
import errno
import sys
from setuptools import setup, Extension
from distutils.command.build_clib import build_clib
from distutils.errors import DistutilsExecError
from distutils.dir_util import mkpath
from distutils.file_util import copy_file
from distutils import log


#
# FIXME: Copied from Python 2.7's subprocess.check_output,
# but with the output= argument to CalledProcessError, which also
# dates to Python 2.7, removed.
#
# When Python 2.6 becomes unsupported, replace this with:
#   from subprocess import check_output, CalledProcessError, check_call
#
from subprocess import Popen, PIPE, CalledProcessError, check_call
def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd)
    return output
#
# FIXME: end section copied from Python 2.7's subprocess.check_output
#


# For ReadTheDocs, do not build the extensions, only install .py files
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

try:
    if sys.argv[1] in ['sdist']: #we need to distribute also c and cpp sources
        raise
    if not os.path.exists('healpy/src/_query_disc.pyx'): #pypi source package does contain the pyx files
        raise
    from Cython.Distutils import build_ext
    import Cython.Compiler.Version as CythonVersion
    from distutils.version import LooseVersion
    assert LooseVersion(CythonVersion.version) >= LooseVersion("0.16")
    ext = "pyx"
    extcpp = "pyx"
except:
  from distutils.command.build_ext import build_ext
  ext = "c"
  extcpp = "cpp"
  print "No Cython >= 0.16 found, defaulting to pregenerated c version."
  
if on_rtd:
    numpy_inc = ''
else:
    from numpy import get_include
    numpy_inc = get_include()


# Test if pkg-config is present. If not, fall back to pykg-config.
try:
    check_output(['pkg-config', '--version'])
    setup_requires = []
except OSError, e:
    if e.errno != errno.ENOENT:
        raise ValueError
    log.warn('pkg-config is not installed, falling back to pykg-config')
    setup_requires = ['pykg-config']
    pykg_config_egg_dir = os.path.join(os.path.realpath('.'), 'pykg_config-1.1.0dev-py2.7.egg')
    os.environ['PKG_CONFIG'] = os.path.join(pykg_config_egg_dir, 'EGG-INFO/scripts/pykg-config.py')
    PYTHONPATH = pykg_config_egg_dir
    if 'PYTHONPATH' in os.environ:
        PYTHONPATH += ':' + os.environ['PYTHONPATH']
    os.environ['PYTHONPATH'] = PYTHONPATH


class build_external_clib(build_clib):
    """Subclass of Distutils' standard build_clib subcommand. Adds support for
    libraries that are installed externally and detected with pkg-config, with
    an optional fallback to build from a local configure-make-install style
    distribution."""

    def __init__(self, dist):
        build_clib.__init__(self, dist)
        self.build_args = {}

    @property
    def _environ(self):
        """Construct an environment dictionary suitable for having pkg-config
        pick up .pc files in the build_clib directory."""
        pkg_config_path = os.path.join(os.path.realpath(self.build_clib), 'lib', 'pkgconfig')
        try:
            pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
        except KeyError:
            pass
        return dict(os.environ, PKG_CONFIG_PATH=pkg_config_path)

    def pkgconfig(self, *packages):
        try:
            PKG_CONFIG = os.environ['PKG_CONFIG']
        except KeyError:
            PKG_CONFIG = 'pkg-config'
        kw = {}
        index_key_flag = (
            (2, '--cflags-only-I', ('include_dirs',)),
            (0, '--cflags-only-other', ('extra_compile_args', 'extra_link_args')),
            (2, '--libs-only-L', ('library_dirs', 'runtime_library_dirs')),
            (2, '--libs-only-l', ('libraries',)),
            (0, '--libs-only-other', ('extra_link_args',)))
        for index, flag, keys in index_key_flag:
            cmd = (PKG_CONFIG, flag) + tuple(packages)
            log.debug('%s', ' '.join(cmd))
            args = [token[index:] for token in check_output(cmd, env=self._environ).split()]
            if args:
                for key in keys:
                    kw.setdefault(key, []).extend(args)
        return kw

    def finalize_options(self):
        """Run 'autoreconf -i' for any bundled libraries to generate the
        configure script."""
        build_clib.finalize_options(self)

        for lib_name, build_info in self.libraries:
            if 'sources' not in build_info:
                log.info("checking if configure script for library '%s' exists", lib_name)
                if not os.path.exists(os.path.join(build_info['local_source'], 'configure')):
                    log.info("running 'autoreconf -i' for library '%s'", lib_name)
                    check_call(['autoreconf', '-i'], cwd=build_info['local_source'])

    def build_library(self, library, pkg_config_name, local_source=None, supports_non_srcdir_builds=True):
        log.info("checking if library '%s' is installed", library)
        try:
            build_args = self.pkgconfig(pkg_config_name)
            log.info("found '%s' installed, using it", library)
        except CalledProcessError:

            # If local_source is not specified, then immediately fail.
            if local_source is None:
                raise DistutilsExecError("library '%s' is not installed", library)

            log.info("building library '%s' from source", library)

            # Determine which compilers we are to use.
            cc = self.compiler.compiler[0]
            cxx = self.compiler.compiler_cxx[0]

            # Use a subdirectory of build_temp as the build directory.
            build_temp = os.path.realpath(os.path.join(self.build_temp, library))

            # Destination for headers and libraries is build_clib.
            build_clib = os.path.realpath(self.build_clib)

            # Create build directories if they do not yet exist.
            mkpath(build_temp)
            mkpath(build_clib)

            if not supports_non_srcdir_builds:
                self._stage_files_recursive(local_source, build_temp)

            # Run configure.
            cmd = [os.path.join(os.path.realpath(local_source), 'configure'),
                '--prefix=' + build_clib,
                'CC=' + cc,
                'CXX=' + cxx,
                '--disable-shared',
                '--with-pic']

            log.info('%s', ' '.join(cmd))
            check_call(cmd, cwd=build_temp, env=self._environ)

            # Run make install.
            cmd = ['make', 'install']
            log.info('%s', ' '.join(cmd))
            check_call(cmd, cwd=build_temp, env=self._environ)

            build_args = self.pkgconfig(pkg_config_name)

        return build_args
        # Done!

    @staticmethod
    def _list_files_recursive(path):
        """Yield paths to all of the files contained within the given path,
        following symlinks."""
        for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
            if not any(p.startswith('.') for p in dirpath.split(os.sep)):
                for filename in filenames:
                    if not filename.startswith('.'):
                        yield os.path.join(dirpath, filename)

    @staticmethod
    def _stage_files_recursive(src, dest):
        """Hard link or copy all of the files in the path src into the path dest.
        Subdirectories are created as needed, and files in dest are overwritten."""
        # Use hard links if they are supported on this system.
        if hasattr(os, 'link'):
            link='hard'
        elif hasattr(os, 'symlink'):
            link='sym'
        else:
            link=None

        for dirpath, dirnames, filenames in os.walk(src, followlinks=True):
            if not any(p.startswith('.') for p in dirpath.split(os.sep)):
                dest_dirpath = os.path.join(dest, dirpath.split(src, 1)[1].lstrip(os.sep))
                mkpath(dest_dirpath)
                for filename in filenames:
                    if not filename.startswith('.'):
                        src_path = os.path.join(dirpath, filename)
                        dest_path = os.path.join(dest_dirpath, filename)
                        if not os.path.exists(dest_path):
                            copy_file(os.path.join(dirpath, filename), os.path.join(dest_dirpath, filename))

    def get_source_files(self):
        """Copied from Distutils' own build_clib, but modified so that it is not
        an error for a build_info dictionary to lack a 'sources' key. If there
        is no 'sources' key, then all files contained within the path given by
        the 'local_sources' value are returned."""
        self.check_library_list(self.libraries)
        filenames = []
        for (lib_name, build_info) in self.libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                sources = list(self._list_files_recursive(build_info['local_source']))

            filenames.extend(sources)
        return filenames

    def build_libraries(self, libraries):
        # Build libraries that have no 'sources' key, accumulating the output
        # from pkg-config.
        for lib_name, build_info in libraries:
            if 'sources' not in build_info:
                for key, value in self.build_library(lib_name, **build_info).iteritems():
                    if key in self.build_args:
                        self.build_args[key].extend(value)
                    else:
                        self.build_args[key] = value

        # Use parent method to build libraries that have a 'sources' key.
        build_clib.build_libraries(self, ((lib_name, build_info)
            for lib_name, build_info in libraries if 'sources' in build_info))


class custom_build_ext(build_ext):
    def run(self):
        # If we were asked to build any C/C++ libraries, add the directory
        # where we built them to the include path. (It's already on the library
        # path.)
        if self.distribution.has_c_libraries():
            self.run_command('build_clib')
            build_clib = self.get_finalized_command('build_clib')
            for key, value in build_clib.build_args.iteritems():
                for ext in self.extensions:
                    if not hasattr(ext, key) or getattr(ext, key) is None:
                        setattr(ext, key, value)
                    else:
                        getattr(ext, key).extend(value)
        build_ext.run(self)

def get_version():
    try:
        exec(open('healpy/version.py'))
    except Exception, e:
        print e
        raise ValueError('Error getting revision number from '
                         'healpy/version.py')
    return __version__

healpy_pixel_lib_src = '_healpy_pixel_lib.cc'
healpy_spht_src = '_healpy_sph_transform_lib.cc'
healpy_fitsio_src = '_healpy_fitsio_lib.cc'

#start with base extension
pixel_lib = Extension('healpy._healpy_pixel_lib',
                      sources=[join('healpy','src', healpy_pixel_lib_src)],
                      include_dirs=[numpy_inc]
                      )

spht_lib = Extension('healpy._healpy_sph_transform_lib',
                     sources=[join('healpy','src', healpy_spht_src)],
                     include_dirs=[numpy_inc],
                     )

hfits_lib = Extension('healpy._healpy_fitsio_lib',
                      sources=[join('healpy','src', healpy_fitsio_src)],
                      include_dirs=[numpy_inc],
                      )

if on_rtd:
    libraries = []
    cmdclass = {}
    extension_list = []
else:
    cmdclass = {'build_ext': custom_build_ext, 'build_clib': build_external_clib}
    libraries = [
        ('cfitsio', {
        'pkg_config_name': 'cfitsio',
        'local_source': 'cfitsiocopy',
        'supports_non_srcdir_builds': False}),
        ('healpix_cxx', {
        'pkg_config_name': 'healpix_cxx',
        'local_source': 'healpixcxx/src/cxx/autotools'})
    ]
    extension_list = [pixel_lib, spht_lib, hfits_lib,
                      Extension("healpy._query_disc",
                                ['healpy/src/_query_disc.'+extcpp],
                                include_dirs=[numpy_inc],
                                language='c++'),
                      Extension("healpy._sphtools", 
                                ['healpy/src/_sphtools.'+extcpp],
                                include_dirs=[numpy_inc],
                                language='c++'),
                      Extension("healpy._pixelfunc", 
                                ['healpy/src/_pixelfunc.'+extcpp],
                                include_dirs=[numpy_inc],
                                language='c++'),
                      ]
    for e in extension_list[-3:]: #extra setup for Cython extensions
        e.pyrex_directives = {"embedsignature": True}
setup(name='healpy',
      version=get_version(),
      description='Healpix tools package for Python',
      author='C. Rosset, A. Zonca',
      author_email='cyrille.rosset@apc.univ-paris-diderot.fr',
      url='http://github.com/healpy',
      packages=['healpy','healpy.test'],
      libraries=libraries,
      py_modules=['healpy.pixelfunc','healpy.sphtfunc',
                  'healpy.visufunc','healpy.fitsfunc',
                  'healpy.projector','healpy.rotator',
                  'healpy.projaxes','healpy.version'],
      cmdclass = cmdclass,
      ext_modules = extension_list,
      package_data = {'healpy': ['data/*.fits', 'data/totcls.dat', 'test/data/*.fits', 'test/data/*.sh']},
      setup_requires=setup_requires,
      install_requires=['pyfits'],
      dependency_links=['https://gist.github.com/lpsinger/5044148/raw/pykg_config-1.1.0dev-py2.7.egg'],
      license='GPLv2'
      )
