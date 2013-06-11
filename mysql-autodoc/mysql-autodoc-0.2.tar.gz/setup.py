#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
   Setup script for mysql-autodoc
"""
#from distutils.core import setup
from setuptools import setup
import os
README = os.path.join(os.path.dirname(__file__), 'README')

LONG_DESCRIPTION = open(README).read() + '\n\n'

setup(name='mysql-autodoc',
      version='0.2',
      author='Ferran Pegueroles Forcadell <ferran@pegueroles.com>, '
             'Alexandre Bénard <abenard@osires.com>',
      author_email='ferran@pegueroles.com',
      maintainer='Ferran Pegueroles Forcadell',
      maintainer_email='ferran@pegueroles.com',
      description='Generate HTML documentation from a mysql database',
      url='http://www.pegueroles.com/',
      long_description=LONG_DESCRIPTION,
      license='GPL',
      platforms='linux,windows',
      download_url='https://bitbucket.org/ferranp/mysql-autodoc/downloads',
      packages=["mysql_autodoc"],
      package_dir={'mysql_autodoc': 'mysql_autodoc'},
      package_data={'mysql_autodoc': ['db.tmpl']},
      entry_points={
          'console_scripts': ['mysql-autodoc = mysql_autodoc:main'],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Utilities',
          'Topic :: Documentation',
          ],
      install_requires=[
          'Jinja2>=2.4',
          'mysql-connector-python>=1.0',
          ],
      )
