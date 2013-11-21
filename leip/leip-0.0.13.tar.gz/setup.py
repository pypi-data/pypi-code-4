#!/usr/bin/env python

from setuptools import setup, find_packages

DESCRIPTION = """
Ultralightweight python CLI framework
"""

entry_points = {
    'console_scripts': [
        'leip = leip.cli:dispatch'
        ]}

setup(name='leip',
      version='0.0.13',
      description=DESCRIPTION,
      author='Mark Fiers',
      entry_points = entry_points,
      author_email='mark.fiers.42@gmail.com',
      url='http://mfiers.github.com/Leip',
      packages=find_packages(),
      #tests_require = ['tox'],
      #cmdclass = {'test': Tox},
      requires=[
          'Yaco (>=0.1.11)',
      ],
      package_dir={'Leip': 'leip'},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          #'Programming Language :: Python :: 3',
          #'Programming Language :: Python :: 3.3',
      ]
    )
