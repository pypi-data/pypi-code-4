# This file is part of longtang.
# Copyright 2013, Guillermo Szeliga.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import os
from setuptools import setup, find_packages

#nosetest fix: http://stackoverflow.com/questions/9352656/python-assertionerror-when-running-nose-tests-with-coverage
from multiprocessing import util

setup(name='longtang',
      version='1.1.0',
      description=
        'Music library organizer and id3 tag manager',
      author='Guillermo Szeliga',
      author_email='gszeliga@gmail.com',
      url='https://bitbucket.org/gszeliga/longtang',
      download_url='',
      license='MIT',
      platforms='ALL',
      long_description=open('README.srt', 'rt').read(),
      install_requires = ['pyacoustid==1.0.0','gevent==0.13.8','nose==1.2.1','PyHamcrest==1.7.1', 'mutagen==1.21','argparse==1.2.1', 'rarfile==2.5'],
      packages=find_packages(),
      scripts=['bin/longtang'],
      test_suite = 'nose.collector',
      keywords = "audio mp3 id3 tag actors music collection musicbrainz",
      classifiers=[
		  'Development Status :: 6 - Mature',
		  'Environment :: Console',
		  'Intended Audience :: End Users/Desktop',
		  'Operating System :: Unix',
		  'Programming Language :: Python :: 2.7',
		  'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Multimedia :: Sound/Audio :: Conversion',
          'Topic :: Multimedia :: Sound/Audio :: Editors',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ],
)
