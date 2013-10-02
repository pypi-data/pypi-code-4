from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

version = "0.0.2"

setup(name='axf',
      version=version,
      description="AXANT ToscaWidget2 Widgets collection",
      long_description=README,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Alessandro Molina',
      author_email='alessandro.molina@axant.it',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'tw2.forms'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
