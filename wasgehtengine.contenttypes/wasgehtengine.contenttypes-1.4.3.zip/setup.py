# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.4.3'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='wasgehtengine.contenttypes',
      version=version,
      description="Wasgehtengine Contenttypes",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Fabian Köster',
      author_email='koesterreich@fastmail.fm',
      url='https://gitorious.org/wasgehtengine',
      license='agpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['wasgehtengine', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity [grok, relations]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.namedfile [blobs]',
          'iso8601',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      #setup_requires=["PasteScript"],
      #paster_plugins=["templer.localcommands"],
      )
