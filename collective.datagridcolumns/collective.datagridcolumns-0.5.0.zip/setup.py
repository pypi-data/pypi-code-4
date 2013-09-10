from setuptools import setup, find_packages
import os, sys

version = '0.5.0'

install_requires = [
    'setuptools',
    # We still not force DataGridField>=1.9.0 because we want this on Plone 3.3 with some hack
    'Products.DataGridField',
    ]

if sys.version_info < (2, 6):
    install_requires.append('simplejson')

setup(name='collective.datagridcolumns',
      version=version,
      description="Additional columns for Plone and DataGridField",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        ],
      keywords='plonegov plone datagridfield archetypes jqueryui widget',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.datagridcolumns',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
