#!/usr/bin/env python
#--coding: utf8--

from setuptools import setup, find_packages

setup(name='pyscrum',
      version='0.1',
      description='Generate scrum boards and charts from .rst task logs.',
      long_description=open('README.rst').read(),
      author='Alex Morozov',
      author_email='inductor2000@mail.ru',
      url='http://github.com/alexmorozov/pyscrum',
      license='GPLv3',
      packages=find_packages(),
      install_requires=['docutils', 'jinja2'],
      entry_points={
          'console_scripts': [
              'mkboard = pyscrum.tools.mkboard:main',
              'mkburndown = pyscrum.tools.mkburndown:main',
          ]
      },
      include_package_data=True,
     )
