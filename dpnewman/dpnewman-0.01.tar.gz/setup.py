# -*- coding: utf-8 -*-
import distribute_setup
distribute_setup.use_setuptools()

from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools.extension import Extension
from setuptools import setup
import numpy as np
import sys
sys.path.append('./src')
sys.path.append('./test')

setup(
    name="dpnewman",
    description="DP-Newman Graph Generative Model",
    version="0.01",
    ext_modules = cythonize([
            Extension(
                'dpnewman',
                ['src/dpnewman.pyx'],
                include_dirs = [np.get_include()]
                )
            ]),
    cmdclass = {'build_ext': build_ext},
    test_suite = 'test_dpnewman.suite',
    install_requires = ['distribute', 'cython','numpy','scipy'],
    )

