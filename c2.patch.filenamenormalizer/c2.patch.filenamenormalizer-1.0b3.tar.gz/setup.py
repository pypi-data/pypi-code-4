from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='c2.patch.filenamenormalizer',
      version=version,
      description="This patch product is for downloaded filename become strange ascii code in muluti-byte languages on Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                          open(os.path.join("docs", "INSTALL.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Patch Japanese normalizer',
      author='Manabu Terada',
      author_email='terada@cmscom.jp',
      url='http://www.cmscom.jp',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.patch'],
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
      )
