import os.path
import sys, glob, re, shutil

########################################################################
########################################################################
## Import setuptools
## Use existing setuptools, otherwise try ez_setup.
try:
    import setuptools
except ImportError:
    ## try to get via ez_setup
    ## ez_setup did not work on all machines tested as
    ## it uses curl with https protocol, which is not
    ## enabled in ScientificLinux
    import ez_setup
    ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension

from Cython.Distutils import build_ext
from Cython.Build import cythonize

classifiers="""
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

# monkey-patch for parallel compilation
# see: http://stackoverflow.com/questions/11013851/speeding-up-build-process-with-distutils
def parallelCCompile(self, sources, 
                     output_dir=None, macros=None, 
                     include_dirs=None, debug=0, 
                     extra_preargs=None, extra_postargs=None, depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build =  self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    N=2 # number of parallel compilations
    import multiprocessing.pool
    def _single_compile(obj):
        try: src, ext = build[obj]
        except KeyError: return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    # convert to list, imap is evaluated on-demand
    list(multiprocessing.pool.ThreadPool(N).imap(_single_compile,objects))
    return objects
#import distutils.ccompiler
#distutils.ccompiler.CCompiler.compile=parallelCCompile


alignlib = [ Extension( 
    # name of extension
    "alignlib_lite",                 
    # filename of our Pyrex/Cython source
    ["alignlib_lite.pyx"] + glob.glob("alignlib_src/*.cpp"),           
    # this causes Pyrex/Cython to create C++ source
    language="c++",              
    # usual stuff
    include_dirs=['alignlib_src'],          
    libraries=[],             
    extra_link_args=[],       
    cmdclass = {'build_ext': build_ext}
    ) ] 

setup(## package information
    name='alignlib-lite',
    version='0.2.1',
    description='alignlib-lite - simple wrapper around alignlib C++ library for sequence alignment',
    author='Andreas Heger',
    author_email='andreas.heger@gmail.com',
    license="BSD",
    platforms=["any",],
    keywords="Sequence alignment",
    long_description='alignlib - python wrapped C++ library around sequence alignment',
    classifiers = filter(None, classifiers.split("\n")),
    url="http://sourceforge.net/projects/alignlib/",
    ## package contents
    packages=None,
    package_dir=None,
    scripts = None,
    package_data = None,
    data_files = None,
    include_package_data = True,
    ## dependencies
    install_requires=[],
    ## extension modules
    ext_modules=alignlib,
    cmdclass = {'build_ext': build_ext},
    ## other options
    zip_safe = False,
    )

