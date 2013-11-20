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
long_description = open(join(dirname(__file__), 'README.rst')).read()
#long_description = """VCF2Networks is a python script that allows to apply the concept of Genotype Network to Single Nucleotide Polymorphism data.
#
#Read more at https://bitbucket.org/dalloliogm/vcf2networks , or at http://pythonhosted.org/vcf2networks/
#
#
#Note on installation: this module depends on the python-igraph library, which requires a C igraph library which must be compiled separately. See https://pypi.python.org/pypi/python-igraph for more instructions. See also https://bitbucket.org/dalloliogm/vcf2networks/src/tip/docs/installing.rst for our tips.
#"""

setup(name = 'vcf2networks',
    version = src.__version__,
    description = 'calculate Genotype Networks from VCF files',
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
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    keywords='genetics vcf population_genetics bioinformatics networks genotype_networks',
    license='GPL',

    entry_points={
        'console_scripts':
            ['vcf2networks = src.vcf2networks:main']
        },

    install_requires=[
#        'setuptools',
        'python-igraph',
        'numpy',
        'PyYAML'
        ],
)



