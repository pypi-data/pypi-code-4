from setuptools import setup, find_packages
import os

version = '2.0b4'

setup(name='Products.PloneTableless',
      version=version,
      description="Plone Tableless provides a completly tableless version of the Plone Default theme",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone theme tableless',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='https://github.com/Raptus/Products.PloneTableless',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plonetheme.classic'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
