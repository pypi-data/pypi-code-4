from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.portlet.explore',
      version=version,
      description="A navigation portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jarn',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://www.jarn.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=["collective", 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "plone.app.layout",
          "plone.app.portlets",
          "plone.portlets",
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
