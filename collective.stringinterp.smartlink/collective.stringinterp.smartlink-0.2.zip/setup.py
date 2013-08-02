from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.stringinterp.smartlink',
      version=version,
      description="Plone string interpolation override for URLs, with backend-frontend support",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        ],
      keywords='plone plonegov e-mail string interpolation',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.stringinterp.smartlink',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.stringinterp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.stringinterp',
          'redturtle.smartlink>=1.1.0',
          'plone.app.discussion',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
