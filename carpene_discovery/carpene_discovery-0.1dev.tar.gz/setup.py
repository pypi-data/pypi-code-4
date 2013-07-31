from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='carpene_discovery',
      version=version,
      description="Python implementation of the Carpene IPv6 host enumeration algorithm",
      long_description=open('README').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ipv6 host-discovery carpene-algorithm',
      author='Clinton Carpene',
      author_email='c.carpene@ecu.edu.au',
      url='carpene.id.au',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
