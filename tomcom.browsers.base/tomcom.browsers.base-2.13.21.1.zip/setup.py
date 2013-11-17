from setuptools import setup, find_packages

version = '2.13.21.1'

setup(name='tomcom.browsers.base',
      version=version,
      description='Reduce seperate importing of browser requirements',
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
      keywords='browser base tomcom',
      author='Tomcom GmbH',
      author_email='info@tomcom.de',
      url='https://github.com/tomcom-de/tomcom.browsers.base.git',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.browsers'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'Zope2',
        'z3c.autoinclude',
      ],
      extras_require={'test': [
        'collective.testcaselayer',
      ]},
      platforms='Any',
      zip_safe=False,
      entry_points='''
[z3c.autoinclude.plugin]
target = zope
''',
)