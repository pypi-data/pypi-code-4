# -*- coding: utf-8 -*-
"""
This module contains the tool of emencia.recipe.patch
"""
from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read() + '\n'
    + '\n' +
   'Download\n'
    '********\n'
    )
entry_point = 'emencia.recipe.patch:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='emencia.recipe.patch',
      version=version,
      description="recipe for patching eggs",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='buildout recipe patch',
      author='Rok Garbas',
      author_email='rok.garbas@gmail.com',
      maintainer='J. David Ibanez',
      maintainer_email='jdavid@emencia.com',
      url='http://github.com/emencia/emencia.recipe.patch',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['emencia', 'emencia.recipe'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'zc.recipe.egg',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'emencia.recipe.patch.tests.test_docs.test_suite',
      entry_points=entry_points,
      zip_safe = True,
      )
