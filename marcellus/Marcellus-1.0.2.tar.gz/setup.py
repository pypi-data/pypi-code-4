# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='Marcellus',
      version='1.0.2',
      author=u'León Domingo',
      author_email='leon@codevince.dev',
      description='Utilities for Quentin projects',
      #license=???,
      keywords='marcellus codevince web',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Topic :: Utilities',
      ],
      url='http://www.codevince.com',
      packages=['marcellus',
                'marcellus.postgres',
                'marcellus.templates',
                ],
      package_data={
          'marcellus.templates': ['*.xml'],
      },
      install_requires=[
          'psycopg2',
          'sqlalchemy',
          'lxml',
          'xlrd',
          'xlwt',
          'simplejson',
          'jinja2',
      ]
      )
