from setuptools import setup
from setuptools import find_packages

version = '0.1'

setup(name='dummypackage',
      version=version,
      description="",
      long_description="",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["something_else"],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
