from setuptools import setup, find_packages
import os

version = '1.2.3'

setup(name='Products.projectmanager',
      version=version,
      description="A product to manage projects for Plone. By Ecreall.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: User Interfaces",
        "Framework :: Plone",
        ],
      keywords='project manager plone',
      author='Michael Launay and Vincent Fretin',
      author_email='development@ecreall.com',
      url='https://svn.ecreall.com/public/Products.projectmanager',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
