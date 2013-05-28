'''
Created on October 5, 2012

@author: Andrew Cron
'''

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from numpy import get_include
from cyrand import include_dir as rng_inc_dir

setup(name='example',
      version='0.1',
      packages=['example'],
      package_dir={'example': 'example'},
      description='Wrapper to TRNG example',
      package_data={'cytrng': ['*.pyx','*.pxd']},
      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension("example", 
                ["example/example.pyx"],
                include_dirs = [get_include(), '/opt/local/include',
                                rng_inc_dir,'./example', '.'],
                library_dirs = ['/opt/local/lib'],
                               #libraries=["trng4"],
                               language='c++')],
      )
