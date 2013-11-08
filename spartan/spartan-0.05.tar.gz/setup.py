#!/usr/bin/python

import glob
import os
import platform
import subprocess
import sys

from os.path import getmtime, exists

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

#from Cython.Build import cythonize

sources = glob.glob('src/spartan/*.cc') +\
          glob.glob('src/spartan/util/*.cc') +\
          glob.glob('src/simple-rpc/rpc/*.cc') +\
          ['spartan/wrap/spartan.i']

def echo(msg, *args):
  print >>sys.stderr, msg % args 

def mtime(file):
  if exists(file): return getmtime(file)
  return -1


if (mtime('./src/spartan/spartan_service.rpc') > 
    mtime('./src/spartan/spartan_service.h')):
  echo('Building service description')
  subprocess.check_call(
    ' '.join(['./src/simple-rpc/rpc/rpcgen.py',
              './src/spartan/spartan_service.rpc']),
    shell=True)
   

setup(
  name='spartan',
  version='0.05',
  maintainer='Russell Power',
  maintainer_email='russell.power@gmail.com',
  url='http://github.com/rjpower/spartan',
  install_requires=[
    'appdirs',
    'numpy>=1.6',
    'sphinx_bootstrap_theme',                
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: POSIX',
    'Programming Language :: C++',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],
  description='Distributed Numpy-like arrays.',
  package_dir={'': '.'},
  packages=['spartan', 
            'spartan.expr',
            'spartan.wrap',
            'spartan.dense',
            'spartan.sparse'],
  ext_modules=[
    Extension('_spartan_wrap',
              include_dirs=['./src', './src/simple-rpc'],
              sources=sources,
              swig_opts = ['-Isrc', '-modern', '-O', '-c++', '-threads', '-w312,509'],
              extra_compile_args=['-ggdb2', '-std=c++0x',],
              extra_link_args=['-lrt', '/usr/lib/gcc/x86_64-linux-gnu/4.8/libstdc++.a']),
    ]
      # + cythonize('tests/netflix.pyx'),
)
