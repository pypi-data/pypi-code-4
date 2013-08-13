#!/usr/bin/env python
from distutils.core import setup
from comrunner import __version__


setup(name='ComRunner',
      version=__version__,
      description='Commandline runner utility',
      long_description='Commandline runner utility',
      author='Guillaume Dugas',
      author_email='dugas.guillaume@gmail.com',
      url='https://github.com/gdugas/comrunner',
      py_modules=['comrunner'],
      license = 'BSD License',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators'
      ]
     )
