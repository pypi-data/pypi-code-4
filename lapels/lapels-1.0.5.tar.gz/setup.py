'''
Created on Oct 25, 2012

@author: Shunping Huang
'''
from setuptools import setup
#from distutils.core import setup
import lapels.version

setup(
    name='lapels',
    version=lapels.version.__version__,
    description='Lapels - A remapper and annotator of in silico (pseudo)'
                ' genome alignments',
    author='Shunping Huang',
    author_email='mark.sphuang@gmail.com',
    url='http://code.google.com/p/lapels/',
    license='The MIT License',
    platforms=['Linux', ],
    packages=['lapels', ],
    scripts=['lapels/scripts/pylapels', 'lapels/scripts/fixmate'],
    install_requires=['pysam>=0.7.4', 'argparse>=1.2', 'cython>=0.17',
                      'modtools>=0.2.5'],
    dependency_links=[],
    keywords='lapels remap position bam mod',
    long_description='''
Lapels remaps reads aligned to the in silico genome back to the reference
coordinate and annotates variants.

Two files are taken as input:
    (1) a MOD file that is used to generate the in silico genome and
    (2) a BAM file that contains the in silico genome alignments.

Lapels will generate a new BAM file with corrected read positions, adjusted
cigar strings, and annotated tags of variants (eg. SNPs, Insertions, and
Deletions).
''',
)
