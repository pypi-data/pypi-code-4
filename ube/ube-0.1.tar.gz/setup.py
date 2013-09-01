#!/usr/bin/env python

'''
Created on Aug 11, 2013

@author: Nicklas Boerjesson
'''


from setuptools import setup

setup(
    name='ube',
    version='0.1',
    description='Unified Back End(UBE) is a collection of libraries used by the UnifiedBPM system.',
    author='Nicklas Boerjesson',
    author_email='nicklasb_attheold_gmaildotcom',
    long_description="""\
      Unified Back End (UBE) is intended as a shippable back end for Python 3 application development.\n
      UBE has a tree-oriented EAV database structure and XML-based database updater functionality to \n
      create and update that structure and others on Postgres, MySQL, DB2, Oracle and MS SQL Server. \n
      Many components, like the updater, can be used separately.\n 
      The API aims to support CRUD, credentials/rights/permissions and auditing.\n 
      Also it uses AOP extensively and therefore provides some usable decorators.
      """,
    url='http://sourceforge.net/projects/ube/',
    packages=['ube', 'ube.api', 'ube.api.tree', 
      'ube.api.tree.tests', 'ube.common', 'ube.api.tree.resources','ube.api.tree.resources.xml',
      'ube.concerns', 'ube.concerns.tests', 
      'ube.db_upgrader', 'ube.db_upgrader.tests', 
      'ube.db_upgrader.tests.resources', 'ube.db_upgrader.tests.resources.postgres',
      'ube.db_upgrader.xml'],
    package_data = {
        # If any package contains *.txt or *.xml files, include them:
        '': ['*.txt', '*.xml', '*.sql', '*.sh']
    },
    license='BSD',
    install_requires=['qal>=0.1'])