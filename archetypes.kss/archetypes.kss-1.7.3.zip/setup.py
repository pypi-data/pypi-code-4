from setuptools import setup, find_packages
import os

version = '1.7.3'

setup(name='archetypes.kss',
      version=version,
      description="KSS (Kinetic Style Sheets) for Archetypes",
      long_description=open("README.txt").read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['archetypes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.uuid'
      ],
      )
