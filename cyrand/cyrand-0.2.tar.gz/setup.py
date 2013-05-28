'''
Created on October 5, 2012

@author: Andrew Cron
'''

from distutils.core import setup
from distutils.extension import Extension
from numpy import get_include

setup(name='cyrand',
      version='0.2',
      packages=['cyrand'],
      package_dir={'cyrand': 'cyrand'},
      description='Wrapper to Boost random numbers',
      maintainer='Andrew Cron',
      maintainer_email='andrew.j.cron@gmail.com',
      author='Andrew Cron',
      author_email='andrew.j.cron@gmail.com',
      url='https://github.com/andrewcron/cyrand',
      requires=['numpy (>=1.3.0)',
                'scipy (>=0.6)',
                'matplotlib (>=1.0)',
                'cython (>=0.15.1)'],
      package_data={'cyrand': ['*.pyx','*.hpp']},
      )
