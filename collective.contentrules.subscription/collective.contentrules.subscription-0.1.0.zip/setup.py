from setuptools import setup, find_packages
import os

version = '0.1.0'
tests_require = ['plone.app.testing']

setup(name='collective.contentrules.subscription',
      version=version,
      description="A Plone content rule for send e-mail to addresses taken from a subscription list",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone rules mail',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.contentrules.subscription',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'plone.contentrules',
          'collective.z3cform.norobots',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
