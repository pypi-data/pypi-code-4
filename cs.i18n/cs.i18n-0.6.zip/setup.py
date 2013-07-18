from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='cs.i18n',
      version = version,
      description="Some i18n customizations for Plone default language change forms",
      long_description=open(os.path.join('cs', 'i18n', 'README.txt')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone i18n',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://code.codesyntax.com/private/cs.i18n',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',         
          # -*- Extra requirements: -*-
          'plone.browserlayer',
          'plone.app.i18n',
          'plone.memoize',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
