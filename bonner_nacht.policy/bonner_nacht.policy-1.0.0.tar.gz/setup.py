# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='bonner_nacht.policy',
      version=version,
      description="Bonner Nacht Site Policy",
      long_description='',
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
      url='https://gitorious.org/bonner-nacht',
      license='agpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['bonner_nacht', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'wasgehtengine.policy',
          'bonner_nacht.theme',
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
