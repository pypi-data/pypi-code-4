from setuptools import setup, find_packages

version = '4.3.0.2'

tests_require = [
    'plone.app.testing',
    'pyquery'
    ]

setup(name='tomcom.plone.easyvoc',
      version=version,
      description='A easy to use add on to define selectable values with numbered key.',
      long_description=open("README.rst").read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='tomcom plone',
      author='tomcom GmbH',
      author_email='mailto:info@tomcom.de',
      url='https://github.com/tomcom-de/tomcom.plone.easyvoc',
      license='GPL2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.plone'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'tomcom.plone.ptregistry',
        'tomcom.plone.base'
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