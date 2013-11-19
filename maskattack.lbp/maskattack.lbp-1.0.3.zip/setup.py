#!/usr/bin/env python
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Thu Jul  11 12:05:55 CEST 2013

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='maskattack.lbp',
    version='1.0.3',
    description='Texture (LBP) based counter-measures for the 3D MASK ATTACK database',
    url='http://github.com/bioidiap/maskattack.lbp',
    license='GPLv3',
    author='Nesli Erdogmus',
    author_email='nesli.erdogmus@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "maskattack",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.1.0",
      "xbob.db.maskattack", #3D Mask Attack database
    ],

    entry_points={
      'console_scripts': [
        'calclbp.py = maskattack.lbp.script.calclbp:main',
        'cmphistmodels.py = maskattack.lbp.script.cmphistmodels:main',
        'ldatrain_lbp.py = maskattack.lbp.script.ldatrain_lbp:main',
        'svmtrain_lbp.py = maskattack.lbp.script.svmtrain_lbp:main',
        'barplot.py = maskattack.lbp.script.barplot:main',
        ],
      },

)
