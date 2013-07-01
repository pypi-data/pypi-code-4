from setuptools import setup, find_packages
import os

version = '1.0a1'

long_description = (
    open("README.rst").read() + "\n" +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read() + "\n" +
    open("CHANGES.txt").read())

setup(name='raptus.touchswipe',
      version=version,
      description="Provides the jQuery TouchSwipe plugin as Plone JS resource",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='http://github.com/Raptus/raptus.touchswipe',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['raptus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
