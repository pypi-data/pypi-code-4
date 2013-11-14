import os
#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "NAMS",
    version = "0.9.2",
    author = "Andre O Falcao and Ana L. Teixeira",
    author_email = "afalcao@di.fc.ul.pt; ateixeira@lasige.di.fc.ul.pt",
    description = ("NAMS is a module to calculate similarity between molecules based on the structural/topological relationships of each atom towards all the others within a molecule."),
    license = read("LICENSE.txt"),
    keywords = "molecular similarity, chemoinformatics, atom matching, structural similarity",
    url = "http://nams.lasige.di.fc.ul.pt/",
    packages=['nams', 'bin'],
    scripts=['bin/tester_chirality.py','bin/tester_doubleb_e_z.py', 'bin/tester_nams.py'],
    package_data={'nams': ['data/*.*']},
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
)
