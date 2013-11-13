from setuptools import setup, find_packages
import os

name = 'seantis.web'
description = (
    "The seantis website."
)
version = '0.3'

long_description = (
    open('README.rst').read()
  )

setup(name=name,
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone seantis website',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/seantis/seantis.web',
      license='gpl',
      packages=find_packages('.'),
      namespace_packages=['seantis', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plone.app.themingplugins',
          'Products.ContentWellPortlets',
          'collective.portlet.embed',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
