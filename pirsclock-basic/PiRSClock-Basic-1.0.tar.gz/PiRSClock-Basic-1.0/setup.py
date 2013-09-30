#! /usr/bin/env python

from distutils.core import setup
from setuptools import setup
setup(name='PiRSClock-Basic',
      version='1.0',
      description='Raspberry Pi Radio Studio Clock Basic Version',
      author='Peter Symonds',
      author_email='peter@engineeringradio.co.uk',
      url='http://github.com/Engineeringradio/pirsclockbasic',
      scripts=['pirsclockbasic'],
      requires=['pygame'],
      install_requires=['pygame'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Console :: Framebuffer',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Customer Service',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Operating System :: POSIX :: Linux',
          'Topic :: Utilities',
          ],
      )
