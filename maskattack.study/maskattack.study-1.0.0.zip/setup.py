#!/usr/bin/env python
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Thu Jul  11 12:05:55 CEST 2013

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires='xbob.extension'))
from xbob.extension import Extension, build_ext

import os
vtk_install_prefix = os.environ.get('VTK_INSTALL_PREFIX', None)
vtk_version = os.environ.get('VTK_VERSION', None)

if vtk_version is None:
  import vtk
  vtk_version = '.'.join(vtk.vtkVersion.GetVTKVersion().split('.')[:2])
else:
  vtk_version = '.'.join(vtk_version.split('.')[:2])
  
vtk_version = 'vtk-' + vtk_version
 
include_dirs = []
library_dirs = []

if vtk_install_prefix is not None:
  include_dirs.append(os.path.join(vtk_install_prefix, 'include', vtk_version))
  library_dirs.append(os.path.join(vtk_install_prefix, 'lib'))
else:
  usr_dir = os.path.join(os.sep, 'usr', 'include', vtk_version)
  if os.path.exists(usr_dir): include_dirs.append(usr_dir)
  usr_dir = os.path.join(os.sep, 'usr', 'local', 'include', vtk_version)
  if os.path.exists(usr_dir): include_dirs.append(usr_dir)
  usr_dir = os.path.join(os.sep, 'opt', 'local', 'include', vtk_version)
  if os.path.exists(usr_dir): include_dirs.append(usr_dir)
  usr_dir = os.path.join(os.sep, 'sw', 'include', vtk_version)
  if os.path.exists(usr_dir): include_dirs.append(usr_dir)
  usr_dir = os.path.join(os.sep, 'sw', 'local', 'include', vtk_version)
  if os.path.exists(usr_dir): include_dirs.append(usr_dir)
  
if len(include_dirs) == 0:
  raise RuntimeError("Cannot find VTK include directory - please set the environment variable VTK_INSTALL_PREFIX to point to the root of your VTK installation")
 
# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='maskattack.study',
    version='1.0.0',
    description='Accumulate depth frames of 3DMAD database for better face models and analyze verification and spoofing performances of 2D, 2.5D and 3D samples',
    url='http://github.com/bioidiap/maskattack.study',
    license='GPLv3',
    author='Nesli Erdogmus',
    author_email='nesli.erdogmus@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages=[
      "maskattack",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.2.0",
      "xbob.db.maskattack", #3D Mask Attack database
    ],

    entry_points={
      'console_scripts': [
        'rgbd_to_rgbxyz.py = maskattack.study.accumulate.rgbd_to_rgbxyz:main',
        'rgbxyz_to_accumulated.py = maskattack.study.accumulate.rgbxyz_to_accumulated:main',
        'accumulated_to_depth.py = maskattack.study.accumulate.accumulated_to_depth:main',
        'view_accumulated.py = maskattack.study.accumulate.view_accumulated:main',
        'hdf5_to_grayscale.py = maskattack.study.accumulate.hdf5_to_grayscale:main',
        'analyzeLBP.py = maskattack.study.analyze.lbp:main',
        'analyzeTPS.py = maskattack.study.analyze.tps:main',
        'analyzeISV.py = maskattack.study.analyze.isv:main',
        'analyzeICP.py = maskattack.study.analyze.icp:main',
        'analyze_plot.py = maskattack.study.analyze.plot:main',
        'antispoofLBP.py = maskattack.study.antispoof.lbp:main',
        'antispoof_plot.py = maskattack.study.antispoof.plot:main',
        ],
      },
    
    cmdclass = {
      'build_ext': build_ext,
      },

    ext_modules=[
      Extension("maskattack.study.analyze._tps", ["maskattack/study/analyze/ext.cpp",],
        library_dirs = library_dirs,
        include_dirs = include_dirs,
        libraries=['vtkHybrid'],
        define_macros = [ ('VTKVER', vtk_version),]
      )
    ],

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      ],        
)
