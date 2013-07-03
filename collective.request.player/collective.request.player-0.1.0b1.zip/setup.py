from setuptools import setup, find_packages

version = '0.1.0b1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='collective.request.player',
      version=version,
      description="The package replays requests. It's a part of https://github.com/potar/dagger",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='request player',
      author='Poburynnyi Taras (potar)',
      author_email='poburynnyitaras@gmail.com',
      url='http://github.com/potar/collective.request.player',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', 'collective.request'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'requests',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
