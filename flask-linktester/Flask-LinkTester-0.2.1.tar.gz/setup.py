"""
Flask-LinkTester
----------------

TODO.
"""

from setuptools import setup

from version import VERSION

REQUIREMENTS = [
  'Flask',
  'requests',
]

TESTS_REQUIREMENTS = REQUIREMENTS + [
  'Flask-Testing',
  'pep8',
  'travis-solo',
]

CLASSIFIERS = [
  'Development Status :: 3 - Alpha',
  'Environment :: Web Environment',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: BSD License',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
  'Topic :: Software Development :: Libraries :: Python Modules'
]


setup(
  name='Flask-LinkTester',
  version=VERSION,
  url='http://github.com/sfermigier/flask-linktester',
  license='BSD',
  author='Stefane Fermigier',
  author_email='sf@fermigier.com',
  description='Link tester for Flask applications',
  packages=['flask_linktester'],
  test_suite="tests.suite",
  zip_safe=False,
  platforms='any',
  install_requires=REQUIREMENTS,
  tests_require=TESTS_REQUIREMENTS,
  classifiers=CLASSIFIERS,
)
