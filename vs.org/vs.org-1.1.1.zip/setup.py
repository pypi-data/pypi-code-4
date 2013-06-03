# -*- coding: utf-8 -*-
"""
This module contains the tool of vs.org
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' )

tests_require = ['zope.testing']

setup(name='vs.org',
      version=version,
      description="Plone 4 add-on: Representation of organisational structures",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Zope Plone ',
      author='Veit Schiele',
      author_email='vs.org@veit-schiele.de',
      url='http://svn.plone.org/svn/collective/vs.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vs', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'pycountry',
                        'archetypes.referencebrowserwidget',
                        'Products.DataGridField',
                        'Products.MasterSelectWidget',
                        'Products.ATVocabularyManager',
                        ],
      tests_require=tests_require,
      extras_require = {
              'test': [ 'plone.app.testing', 'unittest2' ]
              },
#      test_suite='vs.org.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
