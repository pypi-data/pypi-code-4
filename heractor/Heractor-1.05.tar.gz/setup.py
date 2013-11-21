#!/usr/bin/env python

import os
import setuptools
here = os.path.abspath(os.path.dirname(__file__))
from distutils.core import setup


install_requires = [
        'Jinja2',
        'PyYAML',
        'markdown2'
    ]

setup(name='Heractor',
      version='1.05',
      description='Static site Creator',
      author='Dmitry Vysochin',
      author_email='dmitry.vysochin@gmail.com',
      url='https://github.com/veryevilzed/heractor',
      install_requires=install_requires,
      packages=['heractor', 'heractor.plugins'],
      entry_points = {
            'console_scripts': [
                'heract = heractor.heract:main'
            ]
        }
     )