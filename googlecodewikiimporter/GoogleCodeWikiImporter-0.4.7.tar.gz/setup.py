from setuptools import setup, find_packages

__version__ = '0.4.7'

setup(name='GoogleCodeWikiImporter',
      version=__version__,
      description="Google Code Wiki Importer plugin for the Allura platform",
      long_description="",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Tim Van Steenburgh',
      author_email='tvansteenburgh@gmail.com',
      url='http://sf.net/p/googlecodewikiimporter',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['html2text'],
      entry_points="""
      # -*- Entry points: -*-
      [allura.importers]
      google-code-wiki = googlecodewikiimporter.importer:GoogleCodeWikiImporter
      """,
      )
