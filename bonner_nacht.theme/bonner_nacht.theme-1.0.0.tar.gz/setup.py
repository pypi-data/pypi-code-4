# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='bonner_nacht.theme',
      version=version,
      description="Theme for the Bonner Nacht website",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Fabian Köster',
      author_email='koesterreich@fastmail.fm',
      url='http://www.bonner-nacht.de',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bonner_nacht'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plone.app.themingplugins',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
#     entry_points="""
#     # -*- Entry points: -*-
#     
#     [z3c.autoinclude.plugin]
#     target = plone
#     """,
# uncomment these to re-enable support for Paster local commands
#     setup_requires=["PasteScript"],
#     paster_plugins=["ZopeSkel"],
      )
