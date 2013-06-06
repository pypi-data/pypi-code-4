from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plonetheme.corporatevira',
      version=version,
      description="A Plone 4 theme based on plonetheme.corporatemale.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        ],
      keywords='web zope plone theme medialog plonetheme.corporatemale',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='http://github.com/espenmn/plonethmeme.corporatevira',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plonetheme.classic',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
