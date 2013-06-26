from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='nose-long-description',
      version=version,
      description="A nose plugin that combines the name and docstring of a test when describing it.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Matthew J Desmarais',
      author_email='matthew.desmarais@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "nose",
      ],
      entry_points="""
      [nose.plugins.0.10]
      noselongdescription = noselongdescription:LongDescriptionPlugin
      """,
      )
