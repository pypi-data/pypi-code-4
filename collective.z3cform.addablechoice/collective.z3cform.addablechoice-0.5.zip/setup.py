from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='collective.z3cform.addablechoice',
      version=version,
      description="Adds a choice widget with text field to z3cform.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syslab choice widget z3cform',
      author='Johan Beyers',
      author_email='jbeyers@juizi.com',
      url='http://pypi.python.org/pypi/collective.z3cform.addablechoice',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.z3cform',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

