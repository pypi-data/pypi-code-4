from setuptools import setup, find_packages
import sys, os

import passphrasegen

version = '1.1'

setup(name='passphrasegen',
      version=version,
      description=passphrasegen.__doc__.strip(),
      long_description = open('README.rst').read() + '\n'.join(
          '    ' + line for line in
          passphrasegen.parser.format_help().splitlines()),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: Security',
          'Topic :: Utilities',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='password generator passphrase entropy',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='https://github.com/rpatterson/passphrasegen',
      license='GPLv2',
      py_modules=['passphrasegen'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points = {
          'console_scripts': ['passphrasegen = passphrasegen:main']},
      )
