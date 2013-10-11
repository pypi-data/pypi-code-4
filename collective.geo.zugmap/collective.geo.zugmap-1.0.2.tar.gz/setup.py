from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='collective.geo.zugmap',
      version=version,
      description="Zugmap Layer for collective.geo",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='directory plone dexterity',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/collective/collective.geo.zugmap',
      license='GPL v2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.geo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.geo.mapwidget',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
