# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys
from distutils import log

long_desc = ''' '''
requires = ['coards', 'numpy', 'PyYAML', 'NetCDF4', 'DateUtils']

setup(
    name='mom-utils',
    version='1.1.2',
    url='https://github.com/castelao/mom_utils',
    #download_url='https://bitbucket.org/castelao/mom4-utils',
    license='PSF',
    author='Guilherme Castelao, Luiz Irber',
    author_email='guilherme@castelao.net, luiz.irber@gmail.com',
    description='Python utilities for the GFDL\'s numerical model MOM',
    long_description=long_desc,
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    scripts=["bin/mom4_namelist"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
