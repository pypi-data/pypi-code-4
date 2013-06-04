from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.principalsource',
      version=version,
      description="A queriable source for accessing users and/or groups",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone user group principal source',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/plone.principalsource',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.formwidget.query',
          'zope.schema',
          'zope.component',
          'zope.interface',
          'Products.CMFCore',
          'Products.PluggableAuthService',
      ],
      entry_points="""
      """,
      )
