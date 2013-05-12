from setuptools import setup, find_packages
import os

version = '0.5.0'

tests_require=['zope.testing', 'Products.PloneTestCase']

setup(name='Products.PloneboardNotify',
      version=version,
      description="A configurable Plone product for sending e-mails when new messages "
                  "are added to Ploneboard forums",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ploneboard forum notify email',
      author='keul',
      author_email='luca@keul.it',
      url='http://plone.org/products/ploneboardnotify',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Ploneboard',
          'Products.CMFPlone>4.0b1',
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      test_suite = 'Products.PloneboardNotify.tests.test_doctest.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
