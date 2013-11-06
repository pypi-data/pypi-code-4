from distutils.core import setup, Extension
import os

os.system('make objects')

m = Extension('pymtgp64',
              libraries = ['m','cuda','cudart'],
              depends  = ['mtgp64-fast.o','mtgp64dc-param-11213.o','mtgp64-cuda.o'],
              sources   = ['pymtgp64.c'],
              extra_compile_args =  ['-I/usr/local/cuda-5.0/include/','-I.'],
              extra_link_args = ['mtgp64-cuda.o', 'mtgp64dc-param-11213.o' , 'mtgp64-fast.o' ,'-L/usr/local/cuda-5.0/lib64/']
 )

setup(name = 'PyMTGP64',
      version = '1.0',
      description = 'Python version of the Mersenne Twister pseudo-random number generator for Graphic Processor (MTGP)',
      author = 'R. Samadi',
      author_email = 'reza.samadi@obspm.fr',
      url =  'http://lesia.obspm.fr/',
      long_description = open('README.txt').read(),
      ext_modules =  [m]
      )
