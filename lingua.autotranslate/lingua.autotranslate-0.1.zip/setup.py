# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os

version = '0.1'


def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()


setup(name='lingua.autotranslate',
      version=version,
      description="An autotranslation toolkit for .po files using " +
                  "Google Translate API.",
      long_description='\n\n'.join([
          read("README.rst"),
          read("docs", "CONTRIBUTORS.rst"),
          read("docs", "CHANGES.rst"),
      ]),      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='translation po gettext Babel lingua i18n',
      author='Daniel Widerin',
      author_email='daniel@widerin.net',
      url='https://github.com/saily/lingua.autotranslate',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['lingua'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "polib",
          "translate",
          "setuptools",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [console_scripts]
      autotranslate = lingua.autotranslate.translator:AutoTranslator
      """,
      )
