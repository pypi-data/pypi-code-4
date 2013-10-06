# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.9.1'

long_description = '\n\n'.join([read('README.rst'),
                                read('CHANGES.rst')])

setup(name='rt.ploneversions',
      version=version,
      description=("Retrieve information from dist.plone.org to safely "
                   "and easily pin your egg versions"),
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='RedTurtle Technology',
      author_email='sviluppolplone@redturtle.it',
      url='http://www.redturtle.it/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rt'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['nose']},
      entry_points={
          'console_scripts': [
              'ploneversions = rt.ploneversions.ploneversions:main',
          ],
      },
      )
