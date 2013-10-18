from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='zettwerk.clickmap',
      version=version,
      description="Adding a simple clickmap/heatmap to plone 4",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone',
      author='zettwerk GmbH',
      author_email='jk@zettwerk.com',
      url='http://svn.plone.org/svn/collective/zettwerk.ui',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zettwerk'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
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
