from setuptools import setup, find_packages
import sys, os

version = '2.5.0'

setup(name='js.fuelux',
      version=version,
      description="Fanstatic packaging for FuelUX",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='fanstatic fuelux bootstrap twitter',
      author='Dave Sullivan',
      author_email='dave@dave-sullivan.com',
      url='https://github.com/demsullivan/js.fuelux',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "fanstatic",
        "js.bootstrap",
        "setuptools"
      ],
      entry_points={
          'fanstatic.libraries': [
              'fuelux = js.fuelux:library',
              ],
          },
      )
