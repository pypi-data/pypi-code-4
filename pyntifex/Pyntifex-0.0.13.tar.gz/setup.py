#!/usr/bin/python2.7
from distutils.core import setup

setup(
 name = 'Pyntifex',
 version = '0.0.13',
 py_modules = ['password','formatter','solitaire','vtableau','pyrand'],
 author = 'Daniel Dillon Duffield',
 author_email = 'LucianSolaris@gmail.com',
 url = 'https://www.facebook.com/LucianSolaris',
 description = 'NOTE: Package file fixed, source is in package now! - A little encryption keystream, password generation, and tableau lookup distribution centered around Bruce Schneier\'s Pontifex (or Solitaire) keystream algorithm.  This implementation is more flexible than others online, in that one can variate away from 52 members and use objects instead of letters.  Download this if you seek a killer password generating program or would like to use a form of Schneier\'s Pontifex/Solitaire in your program!',
 provides = ['password','formatter','solitaire','vtableau','pyrand'],
 license = 'BSD',
 classifiers = ['Development Status :: 3 - Alpha']
)
