# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='wsgi_chronometer',
      version=version,
      description="Just a wsgi filter for mesure time execution",
      long_description=open('README.rst').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi time filter',
      author=u'Cyprien Le Pannérer',
      author_email='cyplp@free.fr',
      url='https://github.com/cyplp/wsgi_chronometer',
      license='MIT',
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False,
      install_requires=[
          'PasteDeploy',
          "webob",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = wsgi_chronometer:chronometer_filter_factory
      """,
      )
