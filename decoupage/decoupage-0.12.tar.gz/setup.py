from setuptools import setup, find_packages

# use README as long_description
try:
    description = file("README.txt").read()
except IOError:
    description = ''

version = '0.12'

setup(name='decoupage',
      version=version,
      description="Decoupage is the art of decorating an object by gluing colored paper cutouts onto it in combination with special paint effects ... The software decoupage lets you stitch together index pages from filesystem content",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'WebOb',
          'Paste',
          'PasteScript',
          'genshi',
          'martINI>=0.4',
          'contenttransformer>=0.3.3',
          'PyRSS2Gen',
         ],
      dependency_links=['http://www.dalkescientific.com/Python/PyRSS2Gen-1.0.0.tar.gz#egg=PyRSS2Gen'],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      decoupage-templates = decoupage.templates:main
      decoupage-formatters = decoupage.formatters:main

      [paste.app_factory]
      main = decoupage.factory:factory

      [decoupage.formats]
      json = decoupage.formats:JSON
      rss = decoupage.formats:RSS

      [decoupage.formatters]
      all = decoupage.formatters:All
      css = decoupage.formatters:CSS
      datestamp = decoupage.formatters:Datestamp
      describe = decoupage.formatters:FilenameDescription
      icon = decoupage.formatters:Favicon
      ignore = decoupage.formatters:Ignore
      include = decoupage.formatters:Include
      links = decoupage.formatters:Links
      order = decoupage.formatters:Order
      scripts = decoupage.formatters:JavaScript
      sort = decoupage.formatters:Sort
      title = decoupage.formatters:TitleDescription
      up = decoupage.formatters:Up
      """,
      )

