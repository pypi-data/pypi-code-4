# -*- coding: utf-8 -*-
"""
This module contains the tool of redturtle.sqlcontents
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.9.1'

long_description = (
    read('README.rst')
    + '\n\n' +
    read('docs', 'HISTORY.txt')
    + '\n')

tests_require = ['zope.testing']

setup(name='redturtle.sqlcontents',
      version=version,
      description="RedTurtle - SQL Contents",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'Framework :: Plone :: 3.2',
        'Framework :: Plone :: 3.3',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database :: Front-Ends',
        ],
      keywords='Plone',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/redturtle.sqlcontents/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        "Products.DataGridField",
                        "SQLAlchemy"
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='redturtle.sqlcontents.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
#      setup_requires=["PasteScript"],
#      paster_plugins=["ZopeSkel"],
      )
