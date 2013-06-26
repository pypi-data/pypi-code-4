#!/usr/bin/env python
# PPlus setup script

from distutils.core import setup

from pplus import __version__ as VERSION

setup(
        name='PPlus',
        version=VERSION,

        description='A Parallel Python Environment with easy data sharing',
        long_description=open('README').read(),
        author='PPlus developers - SlipGURU',
        author_email='slipguru@disi.unige.it',
        maintainer='Salvatore Masecchia',
        maintainer_email='salvatore.masecchia@disi.unige.it',
        url='http://slipguru.disi.unige.it/Software/PPlus/',

        classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Console',
                'Intended Audience :: Science/Research',
                'Intended Audience :: Developers',
                'Programming Language :: Python',
                'License :: OSI Approved :: BSD License',
                'Topic :: Software Development',
                'Topic :: System :: Distributed Computing',
                'Topic :: Scientific/Engineering :: Bio-Informatics',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS'
        ],
        license = 'new BSD',

        packages=['pplus', 'pplus.core'],
        scripts=['scripts/pplusserver.py'],
        data_files=[('/etc/pplus', ['examples/pplus.cfg'])]
)
