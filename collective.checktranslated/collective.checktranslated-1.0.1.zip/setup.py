from setuptools import setup, find_packages

version = '1.0.1'

setup(name='collective.checktranslated',
      version=version,
      description="This products make a table with all your content and their translation.",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Benoit SUTTOR',
      author_email='bsuttor@cirb.irisnet.be',
      url='https://github.com/CIRB/collective.checktranslated',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      extras_require = {
          'test': [
              'plone.app.testing',
          ]
      },     zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.LinguaPlone',
          'collective.jekyll',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
     )
