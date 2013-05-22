
'''
Created on Jun 7, 2012

@author: Steven Murray
'''

from numpy.distutils.core import setup, Extension
import os
version = '0.4.0'

fort_dft = Extension('PyGS.fort.DFT', ['PyGS/fort/DFT.f90'], 
                     extra_f90_compile_args=['-O3', '-Wall', '-Wtabs','-fopenmp'], 
                     libraries=['gomp'],
                     f2py_options=['--quiet'])
                     
fort_corr = Extension('PyGS.fort.corr', ['PyGS/fort/correlate.f90'], 
                      extra_f90_compile_args=['-O3', '-Wall', '-Wtabs'], 
                      f2py_options=['--quiet'])
                      
fort_lum = Extension('PyGS.fort.luminosity', ['PyGS/fort/lumfunct.f90'],
                     extra_f90_compile_args=['-O3', '-Wall', '-Wtabs'], 
                     f2py_options=['--quiet', 'skip:', 'absmagmax', 'sum_W', 'H', ':'])

import sys
try:
    from numpy.version import version as npversion
except:
    sys.exit("Numpy is not installed!")

if int(npversion.replace('.',''))<162:
    sys.exit("Numpy version is too low, must be >= 1.6.2")
         
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
if __name__ == "__main__":
    setup(name='PyGS',
          version=version,
          requires = ['numpy','pandas','scipy','matplotlib','cosmolopy'],
          author='Steven Murray',
          author_email='steven.jeanette.m@gmail.com',
          description='Interactive program to deal with Galaxy Surveys.',
          long_description = read('README.txt'),
          license = 'BSD',
          url='https://github.com/steven-murray/PyGS',
          ext_modules=[fort_dft, fort_corr, fort_lum],
          packages=['PyGS', 'PyGS.fort']
    )
