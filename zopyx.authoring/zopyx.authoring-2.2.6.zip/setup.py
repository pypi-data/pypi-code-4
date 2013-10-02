# -*- coding: utf-8 -*-
"""
This module contains the tool of zopyx.authoring
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.2.6'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require=['zope.testing']

setup(name='zopyx.authoring',
      version=version,
      description="Produce & Publish Authoring Environment",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://www.produce-and-publish.com',
      license='GNU Public License V2 (GPL 2)',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zopyx.smartprintng.plone',
                        'Products.DataGridField',
#                        'Products.ImageEditor',
#                        'collective.zipfiletransport',
                        'BeautifulSoup',
                        'simpledropbox',
                        'ordereddict',
                        'cssutils',
                        'lxml',
                        'z3c.jbot',
                        ],
      extras_require = {
        'test': ['plone.app.testing', 
                 'unittest2' ]
      },
      test_suite = 'zopyx.authoring.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
