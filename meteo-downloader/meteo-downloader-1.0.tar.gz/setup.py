# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:56:40 2013

@author: kshmirko
"""

#!/usr/bin/env python

from distutils.core import setup

setup(name='meteo-downloader',
      version='1.0',
      description='MeteoFile downloader',
      author='Dr. Hazard_cat',
      author_email='shmirko.konstantin at gmail.com',
      url='None',
      packages=['ios','ncfile','parse'],
      scripts = ['meteogui.py', 'download.py']
     )