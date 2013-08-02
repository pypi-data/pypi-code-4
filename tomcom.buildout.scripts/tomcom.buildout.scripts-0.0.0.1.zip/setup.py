from setuptools import setup, find_packages

version = '0.0.0.1'

setup(name='tomcom.buildout.scripts',
      version=version,
      description='buildout helper scripts',
      long_description=open("README.md").read(),
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
      keywords='buildout helper',
      author='tomcom GmbH',
      author_email='kai.hoppert@tomcom.de',
      url='http://eggserver.tcis.de/tomcom.buildout.scripts',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.buildout'],
      include_package_data=True,
      install_requires=[
        'setuptools',
      ],
      extras_require={'test': [
        'collective.testcaselayer',
      ]},
      entry_points={
          'console_scripts': ['upgrade_version=tomcom.buildout.scripts.upgrade_version:main',
                             'pin_version=tomcom.buildout.scripts.pin_version:main',
                             'get_version_collision=tomcom.buildout.scripts.get_version_collision:main',
                             ]
        },
      platforms='Any',
      zip_safe=False,
)