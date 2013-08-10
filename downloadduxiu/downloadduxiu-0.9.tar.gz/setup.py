#!/usr/bin/env python

from distutils.core import setup
import os

print(os.getcwd())
print([os.path.join('doc',i) for i in os.listdir('doc')]+['README.rst'])
setup(name='downloadduxiu',
      version='0.9',
      description='download images from duxiu and chaoxing library',
      author='Shi Feng',
      author_email='sf.cumt@gmail.com',
      url='https://bitbucket.org/luoboiqingcai/downloadduxiu/',
      py_modules = ['downloadlib','strategy'],
      scripts=['downloadlib.py',],
      data_files=[('Doc/downloadduxiu',[os.path.join('doc',i) for i in os.listdir('doc')]+['README.rst'])],
      requires=['requests'],
      classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License']
      )
