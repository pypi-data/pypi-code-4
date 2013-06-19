import os, sys, pdb, numpy
import distutils.core
# from distutils.core import setup
from setuptools import Extension
from Cython.Distutils import build_ext
from setuptools import setup

version_number = '0.52'
compile_flags = ["-O3"]

if sys.platform != "darwin":
    compile_flags.append("-march=native")


ext_modules = [Extension(
    name="panama.core.lmm.lmm",
    language="c++",
    sources=["panama/core/lmm/lmm.pyx", # to re-generate the cpp from the pyx just uncomment this line
	     # "panama/core/lmm/lmm.cpp",   # and comment this one
	     "panama/core/lmm/c_lmm.cpp",
	     "panama/core/lmm/utils/Gamma.cpp",
	     "panama/core/lmm/utils/FisherF.cpp",
	     "panama/core/lmm/utils/Beta.cpp",
	     "panama/core/lmm/utils/MathFunctions.cpp",
	     "panama/core/lmm/utils/BrentC.cpp"
             ],
    include_dirs = [numpy.get_include()],
    extra_compile_args = compile_flags,
    )]

setup(name = 'panama',
      url = 'http://ml.sheffield.ac.uk/qtl/panama/',
      version = version_number,
      description = 'a novel probabilistic model to account for confounding factors in eQTL studies',
      author = 'Nicolo Fusi*, Oliver Stegle*, Neil Lawrence',
      author_email = 'nicolo.fusi@sheffield.ac.uk',
      packages = ['panama.core', 'panama.core.lmm', 'panama.data'],
      package_data = {'': ['*.csv', '*.pdf', '*.txt']},
      scripts = ['bin/panama'],
      py_modules = ['panama.__init__'],
      cmdclass = {'build_ext': build_ext, 'inplace': True},
      ext_modules = ext_modules,
      install_requires = ['numpy >= 1.6', 'scipy >= 0.9', 'matplotlib >= 1.1', 'ipython >= 0.10', 'Cython', 'pandas', 'GPy', 'pyzmq'],
      license = 'BSD',
      )
