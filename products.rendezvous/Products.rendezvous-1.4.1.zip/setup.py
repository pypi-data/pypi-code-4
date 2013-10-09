import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('docs', 'HISTORY.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )

setup(name='Products.rendezvous',
      version=version,
      description="A timeboard to select a rendez-vous for Plone. By Ecreall.",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        "Framework :: Plone",
        ],
      keywords='',
      author='Vincent Fretin and Michael Launay',
      author_email='development@ecreall.com',
      url='http://pypi.python.org/pypi/Products.rendezvous',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.robotframework',
        ],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
