# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.0'

setup(name='teamrubber.recipe.portbase',
      version=version,
      description="Magical buildout part which can be addressed using offsets to allow a base port",
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
      entry_points = {"zc.buildout": ["default = teamrubber.recipe.portbase:Recipe"]}
      )
