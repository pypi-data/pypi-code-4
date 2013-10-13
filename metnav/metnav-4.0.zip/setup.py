from setuptools import setup, find_packages
import sys, os

version = '4.0'

setup(name='metnav',
      version=version,
      description="Metadata Navigation from eXist and LOM-fr",
      long_description="""\
Metadata navigation from eXist with Learning Objects Metadata LOM LOM-fr
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Plone eXist navigation LOM LOM-fr',
      author='Unis',
      author_email='pratic@ens-lyon.fr',
      url='http://pratic.ens-lyon.fr',
      license='CeCILL-B',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pisa',
          'reportlab',
          'html5lib',
          'z3c.form',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
