import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys, os, pdb

compile_flags = ["-O3"]
# stupid mac is stupid
if sys.platform != "darwin" and sys.platform != "linux2":
    compile_flags.append("-march=native")
elif sys.platform == "darwin":
    os.environ['ARCHFLAGS'] = "-arch i386 -arch x86_64"

ext_modules = [Extension(
    name="lmm",
    language="c++", # grr, mac g++ -dynamic != gcc -dynamic
    sources=["lmm.pyx",
	     "c_lmm.cpp",
             "utils/Gamma.cpp",
             "utils/FisherF.cpp",
             "utils/Beta.cpp",
             "utils/MathFunctions.cpp",
             "utils/BrentC.cpp"
             ],
    include_dirs = [numpy.get_include()],  # .../site-packages/numpy/core/include
    extra_compile_args = compile_flags,
    )]

setup(
    name = 'lmm',
    cmdclass = {'build_ext': build_ext, 'inplace': True},
    ext_modules = ext_modules
    )
