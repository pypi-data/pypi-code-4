from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pylinktester',
      version=version,
      description="a link tester written in python",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python',
      author='yuzhe',
      author_email='lazynight@gmail.com',
      url='http://lazynight.me',
      license='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
      },
      )
