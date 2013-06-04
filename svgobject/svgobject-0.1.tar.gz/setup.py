#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

exec(open('svgobject/_version.py').read())

setup(name='svgobject',
      version=__version__,
      description='Object-oriented library for handling SVG drawings',
      author='Frank Pählke',
      author_email='frank@kette-links.de',
      url='http://www.kette-links.de/software/',
      download_url='http://www.kette-links.de/software/svgobject-'+__version__+'.tar.gz',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],    
      packages=['svgobject'],
      scripts=[],
      requires=[]
     )
