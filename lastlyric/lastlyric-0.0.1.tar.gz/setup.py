
#!/usr/bin/python
#coding=utf-8

import sys
sys.path.append('..')

from distutils.core import setup
from lastlyric import __version__

setup(name='lastlyric',
      version=__version__,
      description='realtime lyric for last.fm',
      long_description=open('README.md').read(),
      author='solos',
      author_email='solos@solos.so',
      py_modules=['lastlyric'],
      scripts=['lastlyric.py'],
      license='MIT',
      platforms=['any'],
      url='https://github.com/solos/lastlyric')
