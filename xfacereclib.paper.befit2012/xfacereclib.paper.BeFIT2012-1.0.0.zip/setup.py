#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 09:27:59 CET 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring adminstrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all parameters that define our package.
setup(

    # Basic information about the project
    name='xfacereclib.paper.BeFIT2012',
    version='1.0.0',
    description='Running the face recognition experiments as given in paper: "An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms".',

    # Additional information of the package
    url='http://github.com/bioidiap/xfacereclib.paper.BeFIT2012',
    license='LICENSE.txt',
    author='Manuel Guenther',
    author_email='manuel.guenther@idiap.ch',

    # The description that is shown on the PyPI page
    long_description=open('README.rst').read(),

    # The definition of what is provided by this package
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install" this package.
    # All packages that are mentioned here, but are not installed on the current system will be installed locally and only visible to the scripts of this package.
    # Don't worry - You won't need adminstrative privileges when using buildout.
    install_requires=[
      'setuptools',                   # the tool to install dependent packages
      'bob == 1.2.0',                 # the base signal processing/machine learning library containing most of the face recognition algorithms
      'PythonFaceEvaluation',         # the patched code of the CSU Face Recognition Resources
      'xfacereclib.extension.CSU',    # the wrapper classes for the CSU Face Recognition Resources
      'facereclib == 1.1.3',          # the tool to actually run all experiments
      'xbob.db.banca',                # the interface to the BANCA database
      'xbob.db.gbu',                  # the interface to the Good, the Bad & the Ugly database
      'matplotlib'                    # plotting utility
    ],

    # This defines a namespace package so that other projects can share this namespace.
    namespace_packages = [
      'xfacereclib',
      'xfacereclib.paper'
    ],

    # Here, the entry points (resources) are registered.
    entry_points={

      # Register two console scripts, one for executing the experiments and one for evaluating the results.
      'console_scripts': [
        'befit2012_execute.py  = xfacereclib.paper.BeFIT2012.execute:main',
        'befit2012_evaluate.py = xfacereclib.paper.BeFIT2012.evaluate:main',
      ],

      # register the particular tools as resources of the FaceRecLib
      'facereclib.database': [
        'b-banca               = xfacereclib.paper.BeFIT2012.configurations:banca',
        'b-gbu-x2              = xfacereclib.paper.BeFIT2012.configurations:gbu_x2',
        'b-gbu-x8              = xfacereclib.paper.BeFIT2012.configurations:gbu_x8',
      ],

      'facereclib.preprocessor': [
        'b-tan-triggs          = xfacereclib.paper.BeFIT2012.configurations:tan_triggs_preprocessor',
        'b-tan-triggs-for-lbp  = xfacereclib.paper.BeFIT2012.configurations:tan_triggs_offset_preprocessor',
        'b-lda-ir              = xfacereclib.paper.BeFIT2012.configurations:ldair_preprocessor',
      ],

      'facereclib.feature_extractor': [
        'b-lgbphs              = xfacereclib.paper.BeFIT2012.configurations:lgbphs_feature_extractor',
        'b-gabor-graph         = xfacereclib.paper.BeFIT2012.configurations:gabor_graph_feature_extractor',
        'b-isv                 = xfacereclib.paper.BeFIT2012.configurations:isv_feature_extractor',
        'b-lda-ir              = xfacereclib.paper.BeFIT2012.configurations:ldair_feature_extractor',
      ],

      'facereclib.tool': [
        'b-lgbphs              = xfacereclib.paper.BeFIT2012.configurations:lgbphs_tool',
        'b-gabor-graph         = xfacereclib.paper.BeFIT2012.configurations:gabor_graph_tool',
        'b-isv                 = xfacereclib.paper.BeFIT2012.configurations:isv_tool',
        'b-lda-ir              = xfacereclib.paper.BeFIT2012.configurations:ldair_tool',
      ],


      'facereclib.grid': [
        'b-simple              = xfacereclib.paper.BeFIT2012.configurations:grid_simple',
        'b-demanding           = xfacereclib.paper.BeFIT2012.configurations:grid_demanding',
        'b-local               = xfacereclib.paper.BeFIT2012.configurations:grid_local',
      ]

      },

    # Classifiers for PyPI
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python :: 2.7',
      'Environment :: Console',
      'Framework :: Buildout',
      'Topic :: Scientific/Engineering',
    ],
)
