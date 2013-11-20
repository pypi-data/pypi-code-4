#!/usr/bin/env python
#
# setup for the VCF2Space suite
#
# use the following to install:
# 
# $: python setup.py install
#

import os
from setuptools import setup
from os.path import join, dirname
import src

scripts = [os.path.join('src', x) for x in os.listdir('src')]
long_description = open(join(dirname(__file__), 'README_pypi.rst')).read(),

setup(name = 'vcf2networks',
    version = src.__version__,
    description = 'a python script to calculate Genotype Networks from VCF files',
    long_description = long_description,
    author = "Giovanni M. Dall'Olio",
    author_email = "giovanni.dallolio@upf.edu",
    url = 'https://bitbucket.org/dalloliogm/vcf2networks',
    download_url = 'https://bitbucket.org/dalloliogm/vcf2networks/get/tip.zip',
    packages=['src'],
#    scripts = scripts,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
#        "Development Status :: 1 - Beta",
#        "Intended Audience :: Bioinformaticians",
#        "Topic :: Bioinformatics",
    ],
    keywords='genetics vcf population_genetics bioinformatics networks genotype_networks',
    license='GPL',

    entry_points={
        'console_scripts':
            ['vcf2network = src.vcf2networks:main']
        },

    install_requires=[
#        'setuptools',
        'python-igraph',
        'numpy',
        'PyYAML'
        ],
)



