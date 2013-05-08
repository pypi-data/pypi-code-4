from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='my_project',
      version=version,
      description="Esta es la descripcion breve",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='package test muestra',
      author='Franco Pellegrini',
      author_email='frapell@gmail.com',
      url='http://google.com',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'caipyrinha',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
