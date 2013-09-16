#!/usr/bin/env python

import os
import glob
from collections import namedtuple

try:
    import setuptools
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()

from numpy.distutils.misc_util import Configuration

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
from distutils.cygwinccompiler import CygwinCCompiler
from distutils.msvccompiler import MSVCCompiler

from ConfigParser import SafeConfigParser


NAME = "orangecontrib.earth"
VERSION = "0.1.1"
DESCRIPTION = "An implementation of MARS algorithm for Orange."
LONG_DESCRIPTION = open("README.rst", "rb").read()
AUTHOR = "Bioinformatics Laboratory, FRI UL"
AUTHOR_EMAIL = "contact@orange.biolab.si"
URL = "https://bitbucket.org/ales_erjavec/orangecontrib-earth"
DOWNLOAD_URL = "https://pypi.python.org/pypi/orangecontrib.earth"
LICENSE = "GPLv3"

PACKAGES = find_packages()


def mno_cygwin_fix(compiler):
    """
    Remove the '-mno-cygwin' flag from a mingw32 compiler commands.
    """
    for name in ["compiler", "compiler_so", "compiler_cxx",
                 "linker_exe", "linker_so"]:
        if "-mno-cygwin" in getattr(compiler, name):
            getattr(compiler, name).remove("-mno-cygwin")


def msvc_force_cpp_fix(compiler):
    """
    Force the MSVCcompiler instance to compile *.c sources as c++.
    """
    # Copy the ext mappings from class members to instance members
    compiler._c_extensions = list(compiler._c_extensions)
    compiler._cpp_extensions = list(compiler._cpp_extensions)
    # make sure a .c file will be compiled as C++.
    compiler._c_extensions.remove(".c")
    compiler._cpp_extensions.append(".c")


class build_ext(_build_ext):
    def run(self):
        # Run make sure the c libraries are build
        # (develop and other commands only call build_ext but we
        # need the libraries to be build before.
        self.run_command("build_clib")
        _build_ext.run(self)

    def build_extensions(self):
        self._customize_compiler()
        _build_ext.build_extensions(self)

    def _customize_compiler(self):
        if isinstance(self.compiler, CygwinCCompiler) and \
                self.compiler.compiler_type == "mingw32":
            mno_cygwin_fix(self.compiler)
        elif isinstance(self.compiler,  MSVCCompiler):
            msvc_force_cpp_fix(self.compiler)


lib_config = namedtuple(
    "lib_config", ["libraries", "library_dirs"])

earth_config = namedtuple("earth_config", ["blas", "R"])


def libs_parse(text):
    return [lib.strip() for lib in text.split(",")]


def dirs_parse(text):
    return text.strip().split(os.path.pathsep)


def parse_lib_opt(parser, section):
    libs, library_dirs = [], []

    if parser.has_option(section, "libraries"):
        libs = libs_parse(parser.get(section, "libraries"))
    if parser.has_option(section, "library_dirs"):
        library_dirs = dirs_parse(parser.get(section, "library_dirs"))

    if libs or library_dirs:
        return lib_config(libs, library_dirs)
    else:
        return None


def site_config():
    blas = R = None
    parser = SafeConfigParser()
    parser.read(["site.cfg",
                 os.path.expanduser("~/.orangecontrib-earth-site.cfg")])

    if parser.has_section("blas_opt"):
        blas = parse_lib_opt(parser, "blas_opt")

    if parser.has_section("R_opt"):
        R = parse_lib_opt(parser, "R_opt")

    return earth_config(blas, R)


def sources(pattern):
    return glob.glob(pattern)


def configuration(parent_package="", top_path=None):
    config = Configuration("earth", parent_package, top_path)
    libraries = []
    library_dirs = []

    site = site_config()

    if site.blas:
        # Link to provided blas library
        libraries += site.blas.libraries
        library_dirs += site.blas.library_dirs
    else:
        # Compile and link the included blas subset
        config.add_library("blas", sources=sources("src/blas/*.c"))

    if site.R:
        # Link to the provided R library
        libraries += site.R.libraries
        library_dirs += site.R.library_dirs
    else:
        config.add_library("R", sources=sources("src/rlib/*.c"))

    config.add_extension(
        "_earth",
        sources=["src/_earth.c"],
        define_macros=[("STANDALONE", 1),
                       ("USE_BLAS", 1),
                       ("MAIN", 1)],
        libraries=libraries,
        library_dirs=library_dirs,
        extra_compile_args=["-std=c99"],
        # export Earth function for ctypes (needed for MSVC)
        export_symbols=["Earth"]
    )

    return config

INSTALL_REQUIRES = (
    "Orange >= 2.7"
)

SETUP_REQUIRES = (
    "setuptools",
    "numpy",
)

KEYWORDS = (
    "mars",
    "earth",
    "multivariate adaptive regression splines",
    "machine learning",
    "orange add-on",
)

CLASSIFIERS = (
    "Environment :: Console",
    "Environment :: Plugins",
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
)

ENTRY_POINTS = {
    "orange.addons": (
        "regression__earth = orangecontrib.earth.earth",
    ),
    "orange.widgets": (
        "Earth = orangecontrib.earth.widgets.OWEarth",
    ),
    "orange.canvas.help": (
        "intersphinx = orangecontrib.earth.widgets:intersphinx",
    ),
    "orange.widgets.feature_score": (
        "_ = orangecontrib.earth.widgets:EARTH_SCORE",
    )
}


def setup_package():
    config = configuration("orangecontrib").todict()
    del config["name"]

    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          download_url=DOWNLOAD_URL,
          license=LICENSE,
          keywords=KEYWORDS,
          classifiers=CLASSIFIERS,
          packages=PACKAGES,
          install_requires=INSTALL_REQUIRES,
          setup_requires=SETUP_REQUIRES,
          entry_points=ENTRY_POINTS,
          zip_safe=False,
          include_package_data=True,
          cmdclass={"build_ext": build_ext},
          **config)

if __name__ == "__main__":
    setup_package()
