from setuptools import setup, find_packages
import os

version = '1.3.0'

setup(name='cciaa.portlet.calendar',
      version=version,
      description="Alternative calendar portlet for Plone that perform some additional search",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='plone plonegov calendar portlet',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/cciaa.portlet.calendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cciaa', 'cciaa.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
