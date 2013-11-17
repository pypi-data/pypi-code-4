from setuptools import setup, find_packages

version = '2.13.21.1'

setup(name='tomcom.patch.getbrowser',
      version=version,
      description='A patch to query a browser on every context',
      long_description=open("README.rst").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Zope2",
          "Intended Audience :: Other Audience",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
        ],
      keywords='tomcom hook get_browser zope2',
      author='Tomcom GmbH',
      author_email='infot@tomcom.de',
      url='https://github.com/tomcom-de/tomcom.patch.getbrowser.git',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.patch'],
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