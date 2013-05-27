from setuptools import setup, find_packages
import os

version = '1.3.3'

setup(name='collective.addthis',
      version=version,
      description="AddThis addon for Plone CMS",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='AddThis',
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@jyu.fi',
      url='https://github.com/collective/collective.addthis',
      license='GPL',
      namespace_packages=['collective'],
      packages=find_packages('src'),
      package_dir = {'': 'src'}, 
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.registry',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['plone.app.testing', 'collective.googleanalytics'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
