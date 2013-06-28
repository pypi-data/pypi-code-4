from setuptools import setup, find_packages

version = '1.0'

setup(name='collective.readitlater',
      version=version,
      description="No time ? Read it later !",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='plone',
      author='Gagaro',
      author_email='gagaro42@gmail.com',
      url='https://github.com/Gagaro/collective.readitlater',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.registry',
          'plone.directives.form',
          'collective.js.datatables',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(
          test=['plone.app.testing', 'plone.app.robotframework'],
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
