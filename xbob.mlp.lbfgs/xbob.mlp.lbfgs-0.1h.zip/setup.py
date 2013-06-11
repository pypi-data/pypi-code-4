#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri May 10 12:34:27 CEST 2013

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.mlp.lbfgs',
    version='0.1h',
    description='L-BFGS-based trainer for the MLP machine of Bob',

    url='http://github.com/bioidiap/xbob.mlp.lbfgs',
    license='GPLv3',
    author='Laurent El Shafey',
    author_email='laurent.el-shafey@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
      'setuptools',
      'bob', # base signal proc./machine learning library
    ],

    namespace_packages = [
      'xbob',
    ],

    entry_points={

      # declare tests to bob
      'bob.test': [
         'mlp.lbfgs = xbob.mlp.lbfgs.test:MLPLbfgsTests',
         ],
      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
)
