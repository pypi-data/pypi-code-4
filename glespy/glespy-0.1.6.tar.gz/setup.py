#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from distutils.core import setup
# import os
try:
    import pandoc
    pandoc.core.PANDOC_PATH = '/usr/bin/pandoc'

    doc = pandoc.Document()
    doc.markdown = open('README.md').read()
    f = open('README.txt', 'w+')
    f.write(doc.rst)
    f.close()

    long_description = open('README.txt').read()
except:
    long_description = ''

setup(
    name='glespy',
    version='0.1.6',
    packages=['glespy', 'glespy.test', 'glespy.tools',
              'glespy.tools.test', 'glespy.test_data',
              'glespy.ext',],
    url='https://pypi.python.org/pypi/glespy/',
    # license='no license yet...',
    author='yarnaid',
    author_email='yarnaid@gmail.com',
    description='Bindings for GLESP for calculations with spherical harmonics',
    keywords='GLESP bindings',
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "License :: Freeware",
        "Natural Language :: Russian",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
