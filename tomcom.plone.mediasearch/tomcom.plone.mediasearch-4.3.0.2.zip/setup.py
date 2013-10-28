from setuptools import setup, find_packages

version = '4.3.0.2'

tests_require = [
    'plone.app.testing',
    'pyquery'
    ]

setup(name='tomcom.plone.mediasearch',
      version=version,
      description='Media search',
      long_description=open("README.rst").read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
        'Framework :: Plone',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='tomcom plone',
      author='tomcom GmbH',
      author_email='mailto:info@tomcom.de',
      url='http://stash.tomcom.de/scm/PLONE/tomcom.plone.mediasearch.git',
      license='GPL2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.plone'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'jarn.jsi18n',
        'tomcom.plone.ptregistry',
        'tomcom.tpcheck',
        'tomcom.pdfpreview',
        'tomcom.adapters.updateactualurl'
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