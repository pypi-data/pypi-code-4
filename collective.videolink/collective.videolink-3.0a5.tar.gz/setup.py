from setuptools import setup, find_packages
import os

version = '3.0a5'

setup(name='collective.videolink',
      version=version,
      description="Display link content type as embedded video, provide a video gallery view",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='David Bain',
      author_email='david.bain@alteroo.com',
      url='http://bitbucket.org/alteroo/collective.videolink',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.prettyphoto',
          'p4a.videoembed',
          'z3c.unconfigure==1.0.1',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,)
