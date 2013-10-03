#!/usr/bin/env python

from distutils.core import setup

setup(name='siqueries',
      version='1.0.8',
      scripts=['siqueries_install', 'siqueries_connect'],
      classifiers = ['Environment :: Console',
                     'Intended Audience :: System Administrators',
                     'License :: Other/Proprietary License',
                     'Natural Language :: English',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.4',
                     'Programming Language :: Python :: 2.5',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: System :: Monitoring',
                     'Topic :: Database',
                     'Topic :: Database :: Database Engines/Servers',
                     ],
      requires=['simplejson'],
      url='http://siqueries.com/',
      author='SiQueries',
      author_email='support@siqueries.com',
      description='Setup wizard and connection client for connecting MySQL/PostgreSQL databases to siqueries.com',
)
