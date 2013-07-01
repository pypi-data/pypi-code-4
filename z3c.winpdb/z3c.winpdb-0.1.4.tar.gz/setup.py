from setuptools import setup, find_packages
import os

version = '0.1.4'

long_description = (
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='z3c.winpdb',
      version=version,
      description="Enable remote debugging with winpdb in Zope / Plone",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Thomas Schilz',
      author_email='thschilz@web.de',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      package_data={'':['*.zcml', 'CHANGES.txt']},
      zip_safe=False,
      install_requires=[
          'setuptools',
          'winpdb',
          'zope.app.appsetup',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
