from setuptools import setup, find_packages

version = '4.3.0.1'

tests_require = [
    'Products.PloneTestCase',
    'pyquery'
    ]

setup(name='tomcom.bootstrap.navbar',
      version=version,
      description='Navbar build fron portal_actions in bootstrap style',
      long_description=open("README.rst").read(),
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='tomcom plone',
      author='tomcom GmbH',
      author_email='mailto:info@tomcom.de',
      url='http://stash.tomcom.de/scm/PLONE/tomcom.bootstrap.navbar.git',
      license='GPL2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.bootstrap'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'Products.PloneTestCase',
        'tomcom.plone.ptregistry',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require,
                     ),
      zip_safe=False,
      entry_points='''
[z3c.autoinclude.plugin]
target = plone
''',
)