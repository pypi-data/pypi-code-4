#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Tue 16 Jul 2013 14:22:33 CEST

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.db.maskattack',
    version='1.0.0a0',
    description='3D Mask Attack Database Access API for Bob',
    url='http://github.com/bioidiap/xbob.db.maskattack',
    license='GPLv3',
    author='Nesli Erdogmus',
    author_email='nesli.erdogmus@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'bob >= 1.1.0',
    ],

    namespace_packages = [
      'xbob',
      'xbob.db',
      ],

    entry_points = {
      # bob database declaration
      'bob.db': [
        'maskattack = xbob.db.maskattack.driver:Interface',
        ],

      # bob unittest declaration
      'bob.test': [
        'maskattack = xbob.db.maskattack.test:MaskAttackDatabaseTest',
        ],
      },

    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)
