#!/usr/bin/env python2

from distutils.core import setup

setup(name='fiabilipy',
      version='2.2',
      description='Learn dependability with python',
      long_description=open('README').read(),
      author='Simon Chabot',
      author_email='simon.chabot@etu.utc.fr',
      url='http://chabotsi.no-ip.org/trapy/project/viewopened/11',
      license='GPLv2+',
      keywords=('dependability', 'availability', 'reliability', 'markov'),
      requires=['numpy', 'scipy'],
      packages=['fiabili'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Education',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Topic :: Scientific/Engineering',
      ]
     )
