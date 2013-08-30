#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
from setuptools.extension import Extension
import glob
import sys
from os.path import join

try:
    import numpy
except ImportError:
    print 'Error: required package \'Numpy\' not found.'
    print '''Numpy is required in order to run this setup script. Install it \
    using your package manager or from numpy.org.

    While you're at it, make sure you have the following dependencies:
    \tpython-numpy
    \tpython-dev
    \topenmpi-bin
    '''
    print 'Numpy is required in order to run this setup script.'
    print 'Install it using your package manager or from numpy.org'
    print '\tex: sudo apt-get install python-numpy'
    print '\tor sudo pip install numpy'
    print 'On Linux, also ensure that the \'python-dev\' package is installed.'
    print '\n For detailed instructions, see documentation in the \'doc\' '\
          'directory'
    sys.exit(1)

def get_ext_modules():
    """Returns a list of extension modules to be build.

    If cython is installed, cython modules are cythonized and the 
    resulting C source code is returned.
    If cython is not installed, pre-cythonized C source code is returned.
    """
    numpy_dirs = numpy.get_include()
    # build cython files
    # try to compile .pyx files if cython is installed
    # otherwise fall back on compiling the pre-cythoned C code
    ext_modules = None
    try:
        from Cython.Build import cythonize
        print 'cythonizing .pyx files'
        ext_modules = cythonize(["pykaryote/sim/simulation.pyx",
                                "pykaryote/sim/environment.pyx",
                                "pykaryote/sim/families.pyx",
                                "pykaryote/sim/complexes.pyx",
                                "pykaryote/sim/complexes.pxd",
                                "pykaryote/sim/organism.pyx",
                                "pykaryote/sim/complexes.pxd",
                                "pykaryote/sim/genome.pyx"
                                ], )
    except ImportError:
        print 'cython not found, building pre-cythoned C code'
    except Exception:
        print 'cythoning failed, falling back on pre-cythoned C code'
    if ext_modules is None:
        ext_modules = [
            Extension("pykaryote.sim.simulation", 
                      ["pykaryote/sim/simulation.c"],
                      include_dirs = [".",numpy_dirs ]),
            Extension("pykaryote.sim.environment",
                      ["pykaryote/sim/environment.c"],
                      include_dirs = [".",numpy_dirs ]),
            Extension("pykaryote.sim.families", ["pykaryote/sim/families.c"],
                      include_dirs = [".",numpy_dirs ]),
            Extension("pykaryote.sim.complexes", ["pykaryote/sim/complexes.c"],
                      include_dirs = [".",numpy_dirs ]),
            Extension("pykaryote.sim.organism", ["pykaryote/sim/organism.c"],
                      include_dirs = [".",numpy_dirs ]),
            Extension("pykaryote.sim.genome", ["pykaryote/sim/genome.c"],
                      include_dirs = [".",numpy_dirs ]),
        ]
    return ext_modules

setup(
	name = "pykaryote",
	packages = ["pykaryote", "pykaryote.sim", "pykaryote.utils",
    'pykaryote.test', 'pykaryote.petri'],
	package_data={
    'pykaryote':['configs/*.cfg'],
    },
    include_package_data = True,
	version = "1.1.1",
	description = "Tools for modeling the evolution of biological complexity",
    long_description=open('README.txt').read(),
	author = "James Lamine, Ethan Van Andel, Peter Vandehaar",
	url = "https://pykaryote.readthedocs.org/en/latest/",
    install_requires = ['matplotlib', 'numpy', 'mpi4py', 'pillow', 'aggdraw'],
    provides = ['pykaryote'],
    scripts = glob.glob('bin/*'),
    classifiers = [
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7", 
            "Programming Language :: Cython",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",  
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering :: Artificial Life",
            "Topic :: Scientific/Engineering :: Physics"
            ],
            ext_modules = get_ext_modules()
    )
