#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from distutils.core import setup
#from distutils.filelist import findall
from setuptools import setup, findall
from sistagen.version import VERSION

def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='sistagen',
      version=VERSION,
      description='Simple Stat Generator',
      long_description=read('README.txt'),
      author='Sławek Lis',
      author_email='lis.slawek@gmail.com',
      license='BSD',
      url='https://launchpad.net/sistagen',
      
      entry_points={'console_scripts': ['sistagen = sistagen.sistagen:main']},
      
      packages=['rrd', 'sistagen'],
      
      data_files=[
            ('/usr/share/sistagen/templates', findall('templates')),
            ('/usr/share/sistagen/examples', findall('examples')),
          ],

     install_requires = [
            'pyparsing>=2.0',
         ],

     classifiers=[
         'Development Status :: 3 - Alpha',
         'Environment :: Console',
         'License :: OSI Approved :: BSD License',
         'Operating System :: OS Independent',
         'Programming Language :: Python',
         'Topic :: System :: Monitoring',
         'Topic :: Utilities',
        ],
     )
