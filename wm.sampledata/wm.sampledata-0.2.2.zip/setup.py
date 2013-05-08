from setuptools import setup, find_packages
import os

version = '0.2.2'

setup(name='wm.sampledata',
      version=version,
      description="UI and utility methods to generate sampledata for Plone projects",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Plone', 
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2', 
        ],
      keywords='plone sampledata generation',
      author='Harald Friessnegger',
      author_email='harald (at) webmeisterei dot com',
      url='https://github.com/collective/wm.sampledata',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
