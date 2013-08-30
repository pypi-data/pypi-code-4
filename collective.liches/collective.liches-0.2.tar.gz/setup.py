from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.liches',
      version=version,
      description="Integrate linkchecker into plone",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.1",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        ],
      keywords='',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/collective/collective.liches',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
      #setup_requires=["PasteScript"],
      #paster_plugins=["ZopeSkel"],
      )
