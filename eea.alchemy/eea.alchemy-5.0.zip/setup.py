""" EEA Alchemy Installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.alchemy'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("EEA Alchemy allows you to bulk auto-discover "
                   "geographical coverage, temporal coverage, keywords "
                   "and more"),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea alchemy tags tagging',
      author='Alin Voinea (Eaudeweb), European Environment Agency (EEA)',
      author_email="webadmin@eea europa eu",
      url='http://svn.eionet.europa.eu/projects/'
          'Zope/browser/trunk/eea.alchemy',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'eea.faceted.vocabularies',
          'collective.js.jqueryui',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
