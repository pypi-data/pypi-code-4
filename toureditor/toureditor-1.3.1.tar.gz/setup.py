#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

# read version number into __version__
exec(open('toureditorlib/_version.py').read())

setup(name='toureditor',
      version=__version__,
      description=(
        'Editor for GPX/CRP tour files and height profiles.\n'
        '\n'
        'Generates nicer output if matplotlib is installed.'),
      author='Frank Pählke',
      author_email='frank@kette-links.de',
      url='http://www.kette-links.de/technik/',
      download_url='http://www.kette-links.de/software/toureditor-'+__version__+'.tar.gz',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: GIS',
          ],
      packages=['toureditorlib'],
      scripts=['toureditor.pyw', 'tourgraph.py'],
      requires=['mx.DateTime','pyttk','gpxdata','svgobject']
     )
