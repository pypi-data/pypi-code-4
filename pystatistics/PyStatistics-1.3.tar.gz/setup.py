#!/usr/bin/env python

from distutils.core import setup, Extension
from glob import glob


source_files = glob('src/*.cpp')
source_files.append('src/bindings/PyStatistics_wrap.cxx')

extension = Extension('_PyStatistics',
                      source_files,
                      language='c++',
                      extra_compile_args=['-std=c++11'])


setup(name='PyStatistics',
      author='Sean Lewis',
      author_email='splewis@utexas.edu',
      url='https://github.com/splewis/statistics-swig-example',
      description='An EXAMPLE of wrapping some C++ code for Python using SWIG - this is not a statistics library!',
      keywords='example SWIG C++ statistics',
      version='1.3',
      ext_modules=[extension],
      package_dir = {'': 'src/bindings'},
      license='MIT',
      py_modules=['PyStatistics'])
