'''
Created on Oct 6, 2013

@author: Shunping Huang
'''
from setuptools import setup
#from distutils.core import setup
import modtools.version

setup(
    name='modtools',
    version=modtools.version.__version__,
    description='Modtools - a tool set for manipulating MOD and pseudogenomes',
    author='Shunping Huang',
    author_email='mark.sphuang@gmail.com',
    url='http://code.google.com/p/mod-tools/',
    license='The MIT License',
    platforms=['Linux', ],
    packages=['modtools'],
    scripts=['modtools/scripts/refmaker', 'modtools/scripts/get_refmeta',
             'modtools/scripts/vcf2mod', 'modtools/scripts/hap2mod',
             'modtools/scripts/insilico',
             'modtools/scripts/modstat', 'modtools/scripts/modmap'],
    install_requires=['pysam>=0.7.4', 'argparse>=1.2', 'cython>=0.17'],
    dependency_links=[],
    keywords='modtools mod',
    long_description='''A tool set for manipulating MOD and pseudogenomes''',
)
