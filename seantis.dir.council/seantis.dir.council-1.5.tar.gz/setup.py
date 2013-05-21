from setuptools import setup, find_packages
import os

version = '1.5'

zug_require = [
    'izug.basetheme',
    'ftw.contentmenu'
]

setup(name='seantis.dir.council',
      version=version,
      description="Directory of Council Members",
      long_description=('\n'.join((
          open("README.md").read(),
          open(os.path.join("docs", "HISTORY.txt")).read()
      ))),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.3',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python',
      ],
      keywords='council directory seantis plone dexterity',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/seantis/seantis.dir.council',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['seantis', 'seantis.dir'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'plone.app.dexterity',
          'collective.autopermission',
          'collective.testcaselayer',
          'collective.dexteritytextindexer',
          'seantis.dir.base>=1.5',
          'ftw.inflator',
          'izug.basetheme'
      ],
      extras_require=dict(zug=zug_require),
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
