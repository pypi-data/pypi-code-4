from setuptools import setup, find_packages

version = '0.5.0rc1'

setup(name='plonesocial.theme',
      version=version,
      description="Plone theme based on Twitter's Bootstrap CSS",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.txt").read()),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=["Programming Language :: Python", ],
      keywords='plone diazo theme',
      author='Guido Stevens / Based on work by Izhar Firdaus',
      author_email='guido.stevens@cosent.net',
      url='https://github.com/cosent/plonesocial.theme',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonesocial'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
