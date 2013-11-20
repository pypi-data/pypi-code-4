# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.2'

setup(name='teamrubber.recipe.relativepath',
      version=version,
      description="Export the base url from which this part was fetched from",
      long_description="",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='Alan Hoey',
      author_email='alan.hoey@teamrubber.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['teamrubber', 'teamrubber.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        ],
      entry_points = {"zc.buildout": ["default = teamrubber.recipe.relativepath:Recipe"]}
      )
