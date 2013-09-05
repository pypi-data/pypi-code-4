from setuptools import setup, find_packages

version = '1.0.6'

setup(name='collective.sortmyfolder',
      version=version,
      description=("Reveal some not-so-hidden Plone feature for sorting "
                   "your folders"),
      long_description=(open("README.rst").read().strip() + "\n\n" +
                        open("CHANGES.rst").read().strip()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.4",
          "Programming Language :: Python :: 2.5",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Development Status :: 5 - Production/Stable",
          ],
      keywords='plone folder sort',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/collective.sortmyfolder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
