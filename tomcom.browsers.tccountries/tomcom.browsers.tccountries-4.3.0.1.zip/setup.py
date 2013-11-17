from setuptools import setup, find_packages

version = '4.3.0.1'

setup(name='tomcom.browsers.tccountries',
      version=version,
      description='',
      long_description=open("README.rst").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Other Audience",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
        ],
      keywords='',
      author='tomcom GmbH',
      author_email='kai.hoppert@tomcom.de',
      url='http://eggserver.tcis.de/tomcom.browsers.tcworkflow',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.browsers'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'tomcom.patch.getbrowser',
        'tomcom.browsers.base',

      ],
      extras_require={'test': [
        'collective.testcaselayer',
      ]},
      platforms='Any',
      zip_safe=False,
      entry_points='''
[z3c.autoinclude.plugin]
target = plone
''',
)