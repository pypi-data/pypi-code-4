from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='raptus.article.imageslider',
      version=version,
      description="Provides components for showing images in jquerytools scrollable carousels.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "MANUAL.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Plone', 
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2', 
        ],
      keywords='',
      author='Harald Friessnegger',
      author_email='harald (at) webmeisterei dot com',
      url='https://github.com/webmeisterei/raptus.article.imageslider',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus', 'raptus.article'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'raptus.article.core',
          'raptus.article.images',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
