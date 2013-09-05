from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='webpype-django',
      version=version,
      description="WebPype functionality for Django",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django webpipe',
      author='AJ Bahnken',
      author_email='aj@ajvb.me',
      url='https://github.com/ajvb/webpype-django',
      license='GNU General Public License v2',
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
