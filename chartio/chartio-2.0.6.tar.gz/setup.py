#!/usr/bin/env python

from distutils.core import setup
from version import __version__

setup(name='chartio',
      version=__version__,
      scripts=['chartio_setup', 'chartio_connect'],
      classifiers = ['Environment :: Console',
                     'Intended Audience :: System Administrators',
                     'License :: Other/Proprietary License',
                     'Natural Language :: English',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.5',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: System :: Monitoring',
                     'Topic :: Database',
                     'Topic :: Database :: Database Engines/Servers',
                     ],
      requires=['simplejson'],
      py_modules = ['version'],
      url='https://chartio.com/',
      author='chartio.com',
      author_email='support@chartio.com',
      description='Setup wizard and connection client for connecting MySQL/PostgreSQL databases to Chartio',
      long_description=open('README.txt').read()
)
