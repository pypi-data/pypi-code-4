# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:56:40 2013

@author: kshmirko
"""

#!/usr/bin/env python

#from distutils.core import setup
from numpy.distutils.core import setup, Extension

setup(name='nimbus-sat',
      version='1.0',
      description='Read Nimbus sat Level3 data',
      author='Dr. Hazard_cat',
      author_email='shmirko.konstantin@gmail.com',
      url='None',
      packages=['nimbus'],
      ext_modules = [Extension('nimbus.n7t',['nimbus/reader_n7t.f'])]
     )