#!/usr/bin/env python
from distutils.core import setup

readme = open('README.rst').read()

setup(name='pygrbl',
      version="0.1",
      
      description='pyGRBL :: A simple way of controlling a CNC with GRBL',
      long_description='', 
      
      author="Alexander Mendez",
      author_email="blue.space@gmail.com",
      url ="https://www.github.com/ajmendez/pygrbl",
      license='license',
      install_requires = ['clint',
                  'argparse'],
      packages = ['pygrbl'],
      scripts = [
          'bin/gcommand',
          'bin/galign',
          'bin/gstream',
          'bin/goptimize',
      ]
     )
