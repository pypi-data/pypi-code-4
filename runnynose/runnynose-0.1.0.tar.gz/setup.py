from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='runnynose',
      version=version,
      description="A continuous nose runner that tracks dependencies",
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
          'astkit>=0.5.2'
      ],
      entry_points="""
      [console_scripts]
      runnynose = runnynose.cmd:main
      
      [nose.plugins.0.10]
      collector = runnynose.plugin:TestCollectorPlugin
      context = runnynose.plugin:TestContextPlugin
      """,
      )
